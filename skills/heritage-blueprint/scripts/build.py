#!/usr/bin/env python3
"""Package a researched scene into one offline HTML file. Python standard library only."""
import argparse
import base64
import html
import json
import re
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
STATES = {'documented', 'reported', 'photo-estimate', 'unknown'}


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def local_file(folder, value):
    path = (folder / value).resolve()
    if not path.is_relative_to(folder.resolve()):
        raise ValueError('Scene resources must be inside the scene folder: ' + value)
    if not path.is_file():
        raise ValueError('Missing scene resource: ' + str(path))
    return path


def check_evidence(data):
    """Check traceability structure, not truth or photographic similarity."""
    if not data.get('scope') or not data.get('sources') or not data.get('claims'):
        raise ValueError('Evidence needs scope, sources and claims; research before building.')
    ids = [s['id'] for s in data['sources']]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate evidence source IDs')
    for source in data['sources']:
        if not source.get('title') or not (source.get('url') or source.get('file')):
            raise ValueError('A source needs a title and a URL or local reference file')
    for claim in data['claims']:
        if claim.get('status') not in STATES or not claim.get('parameter') or not claim.get('basis'):
            raise ValueError('Every claim needs parameter, status and a short basis')
        if claim['status'] != 'unknown' and not claim.get('sources'):
            raise ValueError('Non-unknown claims need source IDs: ' + claim['parameter'])
        if not set(claim.get('sources', [])).issubset(ids):
            raise ValueError('Unresolved evidence source ID: ' + claim['parameter'])


def json_script(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')


def check_offline(content):
    # Metadata citation URLs and ordinary hyperlinks are permitted; runtime resources are not.
    if re.search(r'<(?:script|img|iframe|audio|video|source|link)\b[^>]*(?:src|href)\s*=\s*["\'](?!data:|#)', content, re.I):
        raise ValueError('External resource found; inline all runtime assets')
    if re.search(r'\b(?:fetch|XMLHttpRequest|WebSocket|importScripts)\s*\(|\bimport\s*(?:\(|["\'])|@import\b', content):
        raise ValueError('Network/import code found; keep output offline')
    if re.search(r'url\(\s*["\']?(?!data:|#)[^\s"\')]', content, re.I):
        raise ValueError('Non-embedded CSS asset found')


def build(scene_path, output, force=False):
    scene_path = scene_path.resolve()
    scene = read_json(scene_path)
    for key in ('titleZh', 'titleEn', 'geometry', 'evidence'):
        if not isinstance(scene.get(key), str) or not scene[key].strip():
            raise ValueError('Missing scene field: ' + key)
    if scene.get('schemaVersion') != 1:
        raise ValueError('Use schemaVersion: 1')
    folder = scene_path.parent
    geometry = local_file(folder, scene['geometry']).read_text(encoding='utf-8-sig')
    if re.search(r'</script', geometry, re.I):
        raise ValueError('Geometry must not contain a closing script tag')
    evidence = read_json(local_file(folder, scene['evidence']))
    check_evidence(evidence)
    inset = local_file(folder, scene['inset']).read_text(encoding='utf-8-sig') if scene.get('inset') else ''
    if re.search(r'<script|\bon\w+\s*=|javascript:', inset, re.I):
        raise ValueError('Inset must be static inline HTML/SVG')

    font_dir = SKILL / 'assets/fonts'
    coverage = set(read_json(font_dir / 'coverage.json'))
    font_text = scene['titleZh'] + '展開收起'
    missing = sorted({c for c in font_text if not c.isspace() and ord(c) not in coverage})
    if missing:
        raise ValueError('IBM Plex Sans TC lacks these title/control glyphs: ' + ''.join(missing) +
                         '. Ask for approved traditional spelling or an explicit font alternative; do not silently fall back or enlarge text.')
    encoded = base64.b64encode((font_dir / 'IBMPlexSansTC-Bold.woff2').read_bytes()).decode('ascii')
    ranges = ','.join('U+' + format(ord(c), 'X') for c in sorted(set(font_text)) if not c.isspace())
    face = '@font-face{font-family:"IBM Plex Sans TC";src:url(data:font/woff2;base64,' + encoded + ') format("woff2");font-style:normal;font-weight:700;font-display:swap;unicode-range:' + ranges + '}'
    duration = scene.get('durationMs', 2850)
    if not isinstance(duration, (int, float)) or not 100 <= duration <= 60000:
        raise ValueError('durationMs must be between 100 and 60000')
    tokens = {
        'SCENE_JS': geometry,
        'META_JSON': json_script({'titleZh': scene['titleZh'], 'titleEn': scene['titleEn'], 'fontText': font_text, 'durationMs': duration}),
        'EVIDENCE_JSON': json_script(evidence),
        'FONT_FACE': face,
        'FONT_LICENSE': '<!-- Unmodified IBM Plex Sans TC Bold; only title and action labels use this font.\n' + (font_dir / 'OFL.txt').read_text(encoding='utf-8').replace('--', '—') + '\n-->',
        'PAGE_TITLE': html.escape(scene['titleZh'] + ' / ' + str(scene.get('edition', '01')) + ' — ' + scene['titleEn']),
        'MODEL_LABEL': html.escape(scene['titleZh'] + '结构示意模型 / ' + scene['titleEn'] + ' structural study', quote=True),
        'TITLE_ZH': html.escape(scene['titleZh']),
        'TITLE_EN': html.escape(scene['titleEn']),
        'EDITION': html.escape(str(scene.get('edition', '01'))),
        'INSET': inset,
    }
    template = (SKILL / 'assets/blueprint.template.html').read_text(encoding='utf-8')
    content = re.sub(r'@@([A-Z_]+)@@', lambda match: tokens[match[1]], template)
    check_offline(content)
    if output.exists() and not force:
        raise ValueError('Output exists; use --force only when replacing this output is intended.')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding='utf-8')
    return {'output': str(output.resolve()), 'bytes': output.stat().st_size, 'font': 'IBM Plex Sans TC Bold, original complete WOFF2', 'embeddedGlyphCoverage': True, 'evidenceClaims': len(evidence['claims']), 'historicalAccuracy': 'Requires source and visual review; not established by packaging.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scene', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.scene, args.output, args.force), ensure_ascii=False, indent=2))
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as error:
        parser.exit(1, 'Build stopped: ' + str(error) + '\n')


if __name__ == '__main__':
    main()
