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
MAX_ARCHIVE = 100 * 1024 * 1024
MAX_EXTRACTED = 250 * 1024 * 1024
MAX_FILES = 5000
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
GITHUB = re.compile(r"https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)")


def safe_path(path):
    parts = path.split("/")
    reserved = re.compile(r"(?i)(con|prn|aux|nul|com[1-9¹²³]|lpt[1-9¹²³]|conin\$|conout\$)(?:\..*)?")
    if (len(path.encode()) > 1024 or len(parts) > 32
            or any(not part or part in (".", "..") or part.endswith((" ", "."))
                   or re.search(r'[<>:"\\|?*\x00-\x1f]', part) or reserved.fullmatch(part)
                   for part in parts)):
        raise ValueError(f"unsafe archive path: {path!r}")
    return path


def manifest():
    data = json.loads((ROOT / "marketplace.json").read_text(encoding="utf-8"))
    if data["schemaVersion"] != 1 or not re.fullmatch(r"skills-v[1-9][0-9]*", data["release"]):
        raise ValueError("Invalid schemaVersion or release tag")
    ids, names = set(), set()
    for skill in data["skills"]:
        for key, seen in (("id", ids), ("name", names)):
            value = skill[key]
            if len(value) > 64 or not NAME.fullmatch(value) or value in seen:
                raise ValueError(f"Invalid or duplicate {key}: {value}")
            seen.add(value)
        if (not GITHUB.fullmatch(skill["repository"])
                or not re.fullmatch(r"[0-9a-f]{40}", skill["commit"])
                or not re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", skill["version"])):
            raise ValueError(f"Invalid repository, commit or version for {skill['id']}")
        for field, limit in (("displayName", 100), ("description", 500), ("license", 80)):
            if not (0 < len(skill[field].strip()) <= limit):
                raise ValueError(f"Invalid {field} for {skill['id']}")
        if skill["path"] == "." and not skill.get("include"):
            raise ValueError(f"Root skill needs an explicit file list: {skill['id']}")
    if not data["skills"] or len(data["skills"]) > 100:
        raise ValueError("Catalog must contain 1–100 skills")
    return data


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
            safe_path(path)
            if stat.S_IFMT(item.external_attr >> 16) not in (0, stat.S_IFREG):
                raise ValueError(f"unsafe non-regular file: {path}")
            for index in range(1, len(path.split("/")) + 1):
                part = "/".join(path.split("/")[:index])
                folded = unicodedata.normalize("NFC", part).casefold()
                if folded in aliases and aliases[folded] != part:
                    raise ValueError(f"unsafe path collision: {path}")
                aliases[folded] = part
            if (path == ".vykor-skill-install.json" or path in files
                    or path.endswith("/SKILL.md") or any(p.startswith(path + "/") or path.startswith(p + "/") for p in files)):
                raise ValueError(f"unsafe or duplicate skill file: {path}")
            total += item.file_size
            if len(files) >= MAX_FILES or item.file_size > MAX_ARCHIVE or total > MAX_EXTRACTED:
                raise ValueError("Skill exceeds archive limits")
            files[path] = upstream.read(item)
            if (item.external_attr >> 16) & 0o111:
                executable.add(path)

        for item in upstream.infolist():
            path = item.filename.removeprefix(root)
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
        text = files.get("SKILL.md", b"").decode("utf-8-sig")
        header = re.match(r"---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
        if not header or not re.search(r"^name:[ \t]*" + re.escape(entry["name"]) + r"[ \t]*$", header[1].replace("\r", ""), re.M):
            raise ValueError(f"SKILL.md must declare name: {entry['name']}")
        if "licensePath" in entry:
            license_path = safe_path(entry["licensePath"])
            if prefix + "LICENSE" != license_path or "LICENSE" not in files:
                add("LICENSE", upstream.getinfo(root + license_path))
        elif re.search(r"^license:[ \t]*" + re.escape(entry["license"]) + r"[ \t]*$", header[1].replace("\r", ""), re.M):
            notice = safe_path(entry["licenseNotice"])
            if not notice.startswith("notices/") or "LICENSE" in files:
                raise ValueError("Invalid market license notice")
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
        asset = f"{skill['id']}-{skill['version']}.zip"
        path = output / asset
        package_skill(skill, io.BytesIO(source), path)
        item = {key: skill[key] for key in ("id", "name", "displayName", "description", "version", "license", "requirements") if key in skill}
        item["source"] = {key: skill[key] for key in ("repository", "commit", "path")}
        item["artifact"] = {
            "url": f"https://github.com/{REPO}/releases/download/{data['release']}/{asset}",
            "size": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        index["skills"].append(item)
        print(f"{asset}: {item['artifact']['size']} bytes", flush=True)
    (DIST / "marketplace.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def verified_index():
    index = json.loads((DIST / "marketplace.json").read_text(encoding="utf-8"))
    data = manifest()
    if (index["release"] != data["release"] or index["schemaVersion"] != data["schemaVersion"]
            or len(index["skills"]) != len(data["skills"])):
        raise ValueError("Index differs from manifest")
    for entry, skill in zip(index["skills"], data["skills"]):
        asset = f"{skill['id']}-{skill['version']}.zip"
        artifact = entry["artifact"]
        if (any(entry[key] != skill[key] for key in ("id", "name", "version", "license"))
                or entry["source"] != {key: skill[key] for key in ("repository", "commit", "path")}
                or artifact["url"] != f"https://github.com/{REPO}/releases/download/{data['release']}/{asset}"):
            raise ValueError(f"Index differs from manifest: {asset}")
        path = DIST / "packages" / asset
        content = path.read_bytes()
        if len(content) != artifact["size"] or hashlib.sha256(content).hexdigest() != artifact["sha256"]:
            raise ValueError(f"ZIP digest or size mismatch: {asset}")
        with zipfile.ZipFile(path) as package:
            if package.testzip() or not {"SKILL.md", "LICENSE"} <= set(package.namelist()):
                raise ValueError(f"Invalid ZIP: {asset}")
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
    releases = json.loads(gh("api", f"{endpoint}?per_page=100", "--paginate", "--slurp"))
    release = next((item for page in releases for item in page if item["tag_name"] == tag), None)
    if release is None:
        release = json.loads(gh("api", endpoint, "-X", "POST", "-f", f"tag_name={tag}", "-f", f"name={tag}",
                                "-f", f"target_commitish={os.environ['GITHUB_SHA']}", "-F", "draft=true"))
    for entry in index["skills"]:
        artifact = entry["artifact"]
        asset = artifact["url"].rsplit("/", 1)[1]
        existing = next((item for item in release["assets"] if item["name"] == asset), None)
        if existing is None and release["draft"]:
            gh("release", "upload", tag, str(DIST / "packages" / asset), "--repo", REPO)
        elif (existing is None or existing["size"] != artifact["size"]
                or existing["digest"] != "sha256:" + artifact["sha256"]):
            raise ValueError(f"Existing Release asset differs: {asset}. Use a new release tag.")
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
