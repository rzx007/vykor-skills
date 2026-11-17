import hashlib
import io
import json
import re
import shutil
import stat
import subprocess
import sys
import unicodedata
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPO = "rzx007/vykor-skills"
MAX_CATALOG = 2 * 1024 * 1024
MAX_ARCHIVE = 100 * 1024 * 1024
MAX_EXTRACTED = 250 * 1024 * 1024
MAX_SKILL_MARKDOWN = 1024 * 1024
MAX_FILES = 5000
INSTALL_MARKER = ".vykor-skill-install.json"
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
RELEASE = re.compile(r"skills-v[1-9][0-9]*")
VERSION = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)")
GITHUB = re.compile(r"https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)")
WINDOWS_DEVICE = re.compile(r"(?i)(con|prn|aux|nul|com[1-9¹²³]|lpt[1-9¹²³]|conin\$|conout\$|clock\$)(?:\..*)?")


def catalog_text(value, limit):
    # The host counts UTF-16 code units and treats a BOM as whitespace.
    return (isinstance(value, str) and len(value.encode("utf-16-le")) <= limit * 2
            and any(not char.isspace() and char != "\ufeff" for char in value))


def safe_path(path):
    if not isinstance(path, str):
        raise ValueError(f"unsafe archive path: {path!r}")
    parts = path.split("/")
    if (len(path.encode()) > 1024 or len(parts) > 32
            or any(not part or part in (".", "..") or part.endswith((" ", "."))
                   or re.search(r'[<>:"\\|?*\x00-\x1f]', part) or WINDOWS_DEVICE.fullmatch(part)
                   for part in parts)):
        raise ValueError(f"unsafe archive path: {path!r}")
    return path


def manifest():
    data = json.loads((ROOT / "marketplace.json").read_text(encoding="utf-8"))
    if type(data["schemaVersion"]) is not int or data["schemaVersion"] != 1 or not RELEASE.fullmatch(data["release"]):
        raise ValueError("Invalid schemaVersion or release tag")
    if not isinstance(data["skills"], list) or not 1 <= len(data["skills"]) <= 100:
        raise ValueError("Catalog must contain 1–100 skills")
    names = set()
    for skill in data["skills"]:
        name = skill["name"]
        if (not catalog_text(name, 64) or not NAME.fullmatch(name)
                or WINDOWS_DEVICE.fullmatch(name) or name in names):
            raise ValueError(f"Invalid or duplicate name: {name}")
        names.add(name)
        for field, limit in (("displayName", 100), ("description", 500), ("license", 80),
                             ("requirements", 500), ("repository", 250), ("commit", 40), ("version", 32)):
            if field == "requirements" and field not in skill:
                continue
            if not catalog_text(skill.get(field), limit):
                raise ValueError(f"Invalid {field} for {name}")
        if (not GITHUB.fullmatch(skill["repository"]) or not re.fullmatch(r"[0-9a-f]{40}", skill["commit"])
                or not VERSION.fullmatch(skill["version"])):
            raise ValueError(f"Invalid repository, commit or version for {name}")
        if not catalog_text(skill.get("path"), 1024):
            raise ValueError(f"Invalid source path for {name}")
        if skill["path"] == ".":
            if not skill.get("include"):
                raise ValueError(f"Root skill needs an explicit file list: {name}")
        else:
            safe_path(skill["path"])
    return data


def catalog_entry(skill):
    return {
        "id": skill["name"],
        **{key: skill[key] for key in ("name", "displayName", "description", "version", "license", "requirements")
           if key in skill},
        "source": {key: skill[key] for key in ("repository", "commit", "path")},
    }


def validate_skill_file(path, aliases, mode=0):
    parts = safe_path(path).split("/")
    if (parts[0].lower() == INSTALL_MARKER or (len(parts) > 1 and parts[-1].lower() == "skill.md")
            or stat.S_IFMT(mode) not in (0, stat.S_IFREG)):
        raise ValueError(f"unsafe skill file: {path}")
    for length in range(1, len(parts) + 1):
        part = "/".join(parts[:length])
        folded = unicodedata.normalize("NFC", part).casefold()
        is_file = length == len(parts)
        if folded in aliases and (aliases[folded] != (part, False) or is_file):
            raise ValueError(f"unsafe path collision: {path}")
        aliases[folded] = (part, is_file)
    # The host counts the directories created during extraction as well as files.
    if len(aliases) > MAX_FILES:
        raise ValueError("Skill exceeds archive entry limit")


def skill_header(content, name):
    if not content or len(content) > MAX_SKILL_MARKDOWN:
        raise ValueError("Missing SKILL.md or file exceeds 1 MiB")
    text = content.decode("utf-8")
    header = re.match(r"---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
    if not header or not re.search(r"^name:[ \t]*" + re.escape(name) + r"[ \t]*$", header[1].replace("\r", ""), re.M):
        raise ValueError(f"SKILL.md must declare name: {name}")
    return header[1].replace("\r", "")


def package_skill(entry, source, output):
    include = [safe_path(path) for path in entry.get("include", [])]
    prefix = "" if entry["path"] == "." else safe_path(entry["path"]) + "/"
    files, aliases, needed = {}, {}, set(include)
    executable = set()
    total = 0
    with zipfile.ZipFile(source) as upstream:
        roots = {item.filename.split("/")[0] for item in upstream.infolist()}
        if len(roots) != 1:
            raise ValueError("Expected exactly one GitHub archive root")
        root = roots.pop() + "/"

        def add(path, item):
            nonlocal total
            validate_skill_file(path, aliases, item.external_attr >> 16)
            total += item.file_size
            if item.file_size > MAX_ARCHIVE or total > MAX_EXTRACTED:
                raise ValueError("Skill exceeds archive limits")
            if path == "SKILL.md" and item.file_size > MAX_SKILL_MARKDOWN:
                raise ValueError("SKILL.md exceeds 1 MiB")
            files[path] = upstream.read(item)
            if (item.external_attr >> 16) & 0o111:
                executable.add(path)

        for item in upstream.infolist():
            path = item.orig_filename.removeprefix(root)
            if item.is_dir() or not path.startswith(prefix):
                continue
            path = path[len(prefix):]
            matching = [choice for choice in include if path == choice or path.startswith(choice + "/")]
            if include and not matching:
                continue
            needed.difference_update(matching)
            add(path, item)
        if needed:
            raise ValueError(f"Missing required files or directories: {', '.join(sorted(needed))}")
        header = skill_header(files.get("SKILL.md"), entry["name"])
        if "licensePath" in entry:
            license_path = safe_path(entry["licensePath"])
            if prefix + "LICENSE" != license_path or "LICENSE" not in files:
                add("LICENSE", upstream.getinfo(root + license_path))
        elif re.search(r"^license:[ \t]*" + re.escape(entry["license"]) + r"[ \t]*$", header, re.M):
            notice = safe_path(entry["licenseNotice"])
            if not notice.startswith("notices/") or "LICENSE" in files:
                raise ValueError("Invalid market license notice")
            validate_skill_file("LICENSE", aliases)
            files["LICENSE"] = (ROOT / notice).read_text(encoding="utf-8").encode("utf-8")
        else:
            raise ValueError("Missing upstream license notice")
        if not files["LICENSE"].strip():
            raise ValueError("Empty LICENSE")

    with zipfile.ZipFile(output, "w") as archive:
        for path, content in sorted(files.items()):
            # Stored entries keep bytes deterministic across Python/zlib versions.
            item = zipfile.ZipInfo(path)
            item.create_system = 3
            item.external_attr = (0o100755 if path in executable else 0o100644) << 16
            archive.writestr(item, content)
    if output.stat().st_size > MAX_ARCHIVE:
        raise ValueError("Skill ZIP exceeds 100 MiB")


def build():
    data = manifest()
    output = DIST / "packages"
    output.mkdir(parents=True, exist_ok=True)
    index = {"schemaVersion": 1, "release": data["release"], "skills": []}
    for skill in data["skills"]:
        repo = GITHUB.fullmatch(skill["repository"])[1]
        url = f"https://codeload.github.com/{repo}/zip/{skill['commit']}"
        with urllib.request.urlopen(url, timeout=45) as response:
            source = response.read(MAX_ARCHIVE + 1)
        if len(source) > MAX_ARCHIVE:
            raise ValueError(f"Source archive exceeds 100 MiB: {repo}")
        asset = f"{skill['name']}-{skill['version']}.zip"
        path = output / asset
        package_skill(skill, io.BytesIO(source), path)
        item = catalog_entry(skill)
        item["artifact"] = {
            "url": f"https://github.com/{REPO}/releases/download/{data['release']}/{asset}",
            "size": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        index["skills"].append(item)
        print(f"{asset}: {item['artifact']['size']} bytes", flush=True)
    (DIST / "marketplace.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def verified_index():
    index_path = DIST / "marketplace.json"
    if index_path.stat().st_size > MAX_CATALOG:
        raise ValueError("Index exceeds 2 MiB")
    index = json.loads(index_path.read_text(encoding="utf-8"))
    data = manifest()
    if (index["release"] != data["release"] or type(index["schemaVersion"]) is not int
            or index["schemaVersion"] != data["schemaVersion"] or not isinstance(index["skills"], list)
            or len(index["skills"]) != len(data["skills"])):
        raise ValueError("Index differs from manifest")
    for entry, skill in zip(index["skills"], data["skills"]):
        asset = f"{skill['name']}-{skill['version']}.zip"
        artifact = entry["artifact"]
        if (entry != {**catalog_entry(skill), "artifact": artifact}
                or artifact["url"] != f"https://github.com/{REPO}/releases/download/{data['release']}/{asset}"):
            raise ValueError(f"Index differs from manifest: {asset}")
        path = DIST / "packages" / asset
        if (type(artifact["size"]) is not int or not 0 < artifact["size"] <= MAX_ARCHIVE
                or path.stat().st_size != artifact["size"]):
            raise ValueError(f"ZIP size mismatch: {asset}")
        content = path.read_bytes()
        if len(content) != artifact["size"] or hashlib.sha256(content).hexdigest() != artifact["sha256"]:
            raise ValueError(f"ZIP digest or size mismatch: {asset}")
        with zipfile.ZipFile(io.BytesIO(content)) as package:
            aliases = {}
            for item in package.infolist():
                validate_skill_file(item.orig_filename, aliases, item.external_attr >> 16)
                if item.compress_type != zipfile.ZIP_STORED or item.compress_size != item.file_size:
                    raise ValueError(f"Invalid ZIP entry: {asset}: {item.filename}")
            if package.testzip() or not {"SKILL.md", "LICENSE"} <= set(package.namelist()):
                raise ValueError(f"Invalid ZIP: {asset}")
            if package.getinfo("SKILL.md").file_size > MAX_SKILL_MARKDOWN or not package.read("LICENSE").strip():
                raise ValueError(f"Invalid SKILL.md or LICENSE: {asset}")
            skill_header(package.read("SKILL.md"), skill["name"])
    return index


def gh(*args):
    return subprocess.run(["gh", *args], check=True, text=True, encoding="utf-8", stdout=subprocess.PIPE).stdout


def publish():
    import os

    if (os.environ.get("GITHUB_ACTIONS"), os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_REF")) != ("true", REPO, "refs/heads/main"):
        raise ValueError("Publishing requires the official main branch workflow")
    index = verified_index()
    tag = index["release"]
    endpoint = f"repos/{REPO}/releases"
    pages = json.loads(gh("api", f"{endpoint}?per_page=100", "--paginate", "--slurp"))
    releases = [release for page in pages for release in page]
    release = next((item for item in releases if item["tag_name"] == tag), None)
    artifacts = {entry["artifact"]["url"].rsplit("/", 1)[1]: entry["artifact"] for entry in index["skills"]}
    current_assets = set()
    for previous in releases:
        previous_tag = previous["tag_name"]
        if previous_tag != tag and (previous["draft"] or not RELEASE.fullmatch(previous_tag)):
            continue
        for existing in previous["assets"]:
            asset = existing["name"]
            if previous_tag == tag:
                current_assets.add(asset)
            artifact = artifacts.get(asset)
            if artifact and (existing["size"] != artifact["size"]
                             or existing.get("digest") != "sha256:" + artifact["sha256"]):
                raise ValueError(f"{previous_tag} already has different bytes for {asset}. Use a new skill version.")
    missing = [asset for asset in artifacts if asset not in current_assets]
    if release is not None and not release["draft"] and missing:
        raise ValueError(f"{tag} is already published and lacks {', '.join(missing)}. Use a new release tag.")

    if release is None:
        release = json.loads(gh("api", endpoint, "-X", "POST", "-f", f"tag_name={tag}", "-f", f"name={tag}",
                                "-f", f"target_commitish={os.environ['GITHUB_SHA']}", "-F", "draft=true"))
    for asset in missing:
        gh("release", "upload", tag, str(DIST / "packages" / asset), "--repo", REPO)
    if release["draft"]:
        gh("api", f"{endpoint}/{release['id']}", "-X", "PATCH", "-F", "draft=false")
    public = DIST / "public"
    public.mkdir(exist_ok=True)
    shutil.copyfile(DIST / "marketplace.json", public / "marketplace.json")
    (public / ".nojekyll").touch()
    print(f"Published {tag} with {len(index['skills'])} assets")


if __name__ == "__main__":
    actions = {"build": build, "verify": verified_index, "publish": publish}
    if len(sys.argv) != 2 or sys.argv[1] not in actions:
        sys.exit("Usage: python scripts/market.py {build|verify|publish}")
    actions[sys.argv[1]]()
