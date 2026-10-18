#!/usr/bin/env python3
"""Fourth-object validation harness (I1 -> I4 bridge). Diagnostic only.

Builds S0 = the real Python publication chain with OBJ-9104 (synthetic structural
clone of OBJ-0003, see make_fixture.py) and ONE temp-only change: the legacy
builder's fixed object list gains OBJ-9104. Then applies one mutation per row to
a fresh copy of S0, re-runs the build-site.yml validator steps, and classifies
each row by its DIFFERENCE from the unmutated S0 baseline.

Every row also runs as a POSITIVE CONTROL: the same mutation applied to the
corresponding OBJ-0003 record on a clean three-object build. A control that is
caught there but missed on OBJ-9104 isolates a scope gap; a control missed
there too indicates the mutation or the validator itself is ineffective.

Nothing in the real repository is modified: all work happens in temporary
copies, and a before/after inventory of the checkout is asserted.

S0 is a SIMULATED publisher. A result here does not show that the production
pipeline can publish a fourth object (the unpatched control shows it cannot).

usage: python3 tests/fourth-object/harness.py <output-dir>   (requires PyYAML)
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
WORKFLOW = ROOT / '.github' / 'workflows' / 'build-site.yml'
IGNORE = shutil.ignore_patterns('.git', 'build', 'site', 'node_modules', '__pycache__')
NEW, ORIG = 'OBJ-9104', 'OBJ-0003'
SLUG = {NEW: 'synthetic-fixture-monument', ORIG: 'cuban-american-friendship-urn'}
REAL_PAGES = ['objects/jose-gervasio-artigas/index.html', 'objects/jose-de-san-martin/index.html',
              'objects/cuban-american-friendship-urn/index.html']
BUILDER_OLD = ("OBJECTS=['OBJ-0001','OBJ-0002','OBJ-0003']; SLUGS={'OBJ-0001':'jose-gervasio-artigas',"
               "'OBJ-0002':'jose-de-san-martin','OBJ-0003':'cuban-american-friendship-urn'}")
BUILDER_NEW = ("OBJECTS=['OBJ-0001','OBJ-0002','OBJ-0003','OBJ-9104']; SLUGS={'OBJ-0001':'jose-gervasio-artigas',"
               "'OBJ-0002':'jose-de-san-martin','OBJ-0003':'cuban-american-friendship-urn',"
               "'OBJ-9104':'synthetic-fixture-monument'}")
LAST_SITE_WRITER = 'Enforce shared navigation and alpha state'
TMP = Path(tempfile.mkdtemp(prefix='fourth-object-'))


# ---------------------------------------------------------------- workspace / CI
def repo_inventory(exclude=None):
    out = {}
    for p in sorted(ROOT.rglob('*')):
        rel = p.relative_to(ROOT)
        if exclude is not None and (p == exclude or exclude in p.parents):
            continue
        if p.is_file() and rel.parts[0] not in ('.git', 'build', 'site', 'node_modules') and '__pycache__' not in rel.parts:
            out[str(rel)] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def workspace(tag, transactions=(), patched=False):
    ws = TMP / tag
    shutil.copytree(ROOT, ws, ignore=IGNORE)
    for name, tx in transactions:
        (ws / 'transactions' / name).write_text(json.dumps(tx, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    if patched:
        p = ws / 'scripts' / 'build_site.py'
        s = p.read_text(encoding='utf-8')
        assert s.count(BUILDER_OLD) == 1, 'legacy builder constant not found exactly once'
        p.write_text(s.replace(BUILDER_OLD, BUILDER_NEW), encoding='utf-8')
    return ws


def clone(ws, tag):
    dst = TMP / tag
    shutil.copytree(ws, dst, symlinks=False)
    return dst


def ci_steps():
    steps = yaml.safe_load(WORKFLOW.read_text(encoding='utf-8'))['jobs']['build']['steps']
    return [s for s in steps if 'run' in s]


def run_steps(ws, steps):
    res = {}
    for s in steps:
        env = {k: v for k, v in os.environ.items() if k != 'KNOWLEDGE_DATA_DIR'}
        env.update({k: str(v) for k, v in (s.get('env') or {}).items()})
        r = subprocess.run(['bash', '-e', '-c', s['run']], cwd=ws, env=env, capture_output=True, text=True)
        out = (r.stdout + r.stderr).replace(str(ws), '<WS>').replace(str(TMP), '<TMP>')
        res[s['name']] = {'exit': r.returncode, 'out': out}
    return res


def site_steps(steps):
    names = [s['name'] for s in steps]
    return steps[names.index(LAST_SITE_WRITER) + 1:]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ---------------------------------------------------------------- HTML helpers
def element_span(text, start):
    """(begin, end) of the element whose start tag begins at `start`."""
    name = re.match(r'<([a-zA-Z0-9]+)', text[start:]).group(1)
    depth, pos = 0, start
    tag = re.compile(rf'<(/?){name}\b[^>]*>', re.I)
    for m in tag.finditer(text, start):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return start, m.end()
    raise ValueError(f'unclosed <{name}> at {start}')


def find(text, pattern):
    m = re.search(pattern, text)
    if not m:
        raise AssertionError(f'mutation target not found: {pattern}')
    return m


# ---------------------------------------------------------------- mutations
# Each returns surface evidence proving the mutation reached the artifact.
def page(site, oid):
    return site / 'objects' / SLUG[oid] / 'index.html'


def m_delete_page(site, oid, ids):
    p = page(site, oid)
    existed = p.exists()
    shutil.rmtree(p.parent)
    return {'target': str(p.relative_to(site)), 'before': existed, 'after': p.exists()}


def m_hide_assertion(site, oid, ids):
    p, a = page(site, oid), ids['A04']
    t = p.read_text(encoding='utf-8'); marker = f'data-assertion-id="{a}"'
    before = t.count(marker); t = t.replace(marker, f'data-removed-assertion-id="{a}"', 1)
    p.write_text(t, encoding='utf-8')
    return {'target': marker, 'before': before, 'after': t.count(marker)}


def m_wrong_status(site, oid, ids):
    p, a = page(site, oid), ids['A04']
    t = p.read_text(encoding='utf-8')
    m = find(t, rf'<(?:article|li)[^>]*data-assertion-id="{a}"[^>]*>')
    old = re.search(r'data-computed-status="([^"]+)"', m.group(0)).group(1)
    new_tag = m.group(0).replace(f'data-computed-status="{old}"', 'data-computed-status="MUTATED_STATUS"')
    t = t[:m.start()] + new_tag + t[m.end():]
    p.write_text(t, encoding='utf-8')
    return {'target': f'{a} data-computed-status', 'before': old, 'after': 'MUTATED_STATUS'}


def m_dependency_state(site, oid, ids):
    p, e = page(site, oid), ids['AE15']
    t = p.read_text(encoding='utf-8')
    m = find(t, rf'<li[^>]*data-assertion-evidence-id="{e}"[^>]*data-dependency-state="[^"]+"[^>]*>')
    old = re.search(r'data-dependency-state="([^"]+)"', m.group(0)).group(1)
    t = t[:m.start()] + m.group(0).replace(f'data-dependency-state="{old}"', 'data-dependency-state="MUTATED_STATE"') + t[m.end():]
    p.write_text(t, encoding='utf-8')
    return {'target': f'{e} data-dependency-state', 'before': old, 'after': 'MUTATED_STATE'}


QUALIFIER = 'none recorded; this does not establish independence'


def m_drop_uncertainty(site, oid, ids):
    p, e = page(site, oid), ids['AE07']
    t = p.read_text(encoding='utf-8')
    m = find(t, rf'<li[^>]*data-assertion-evidence-id="{e}"[^>]*>(.*?)</li>')  # same block EPI-003 reads
    block = m.group(0); before = block.count(QUALIFIER)
    new = block.replace(QUALIFIER, 'inheritance not shown')
    p.write_text(t[:m.start()] + new + t[m.end():], encoding='utf-8')
    return {'target': f'{e} first evidence block qualifier', 'before': before, 'after': new.count(QUALIFIER)}


def m_break_lineage(site, oid, ids):
    p, e = page(site, oid), ids['AE01']
    t = p.read_text(encoding='utf-8')
    m = find(t, rf'<li class="claim-lineage-evidence"[^>]*data-assertion-evidence-id="{e}"[^>]*>(.*?)</li>')
    block = m.group(0); before = block.count('Unresolved ancestry')
    new = block.replace('Unresolved ancestry', 'Ancestry not shown')
    p.write_text(t[:m.start()] + new + t[m.end():], encoding='utf-8')
    return {'target': f'{e} claim-lineage terminal label', 'before': before, 'after': new.count('Unresolved ancestry')}


def m_remove_conflict(site, oid, ids):
    p, a = page(site, oid), ids['A01']
    t = p.read_text(encoding='utf-8'); marker = f'data-conflict-assertion-id="{a}"'
    m = find(t, rf'<aside class="material-conflict" {marker}[^>]*>')
    b, e = element_span(t, m.start())
    before = t.count(marker); t = t[:b] + t[e:]
    p.write_text(t, encoding='utf-8')
    return {'target': marker, 'before': before, 'after': t.count(marker)}


def m_move_conflict(site, oid, ids):
    p, a = page(site, oid), ids['A01']
    t = p.read_text(encoding='utf-8')
    w = find(t, rf'<aside class="material-conflict" data-conflict-assertion-id="{a}"[^>]*>')
    wb, we = element_span(t, w.start()); aside = t[wb:we]
    t = t[:wb] + t[we:]
    lin = find(t, rf'<details class="claim-lineage" data-for-assertion-id="{a}"[^>]*>')
    lb, le = element_span(t, lin.start())
    t = t[:le] + aside + t[le:]
    p.write_text(t, encoding='utf-8')
    warn_pos = t.find(f'data-conflict-assertion-id="{a}"'); lin_pos = t.find(f'class="claim-lineage" data-for-assertion-id="{a}"')
    return {'target': f'{a} warning vs claim-lineage order', 'before': 'warning before lineage', 'after': 'warning after lineage' if warn_pos > lin_pos else 'UNCHANGED'}


def m_card_name(site, oid, ids):
    p = site / 'index.html'
    t = p.read_text(encoding='utf-8')
    m = find(t, rf'<article class="card"[^>]*data-object-id="{oid}"[^>]*>')
    b, e = element_span(t, m.start()); card = t[b:e]
    h = find(card, r'<h2>(.*?)</h2>')
    name = re.sub(r'<[^>]+>', '', h.group(1))
    new = card[:h.start()] + h.group(0).replace(name, 'Mutated Card Name') + card[h.end():]
    p.write_text(t[:b] + new + t[e:], encoding='utf-8')
    return {'target': f'homepage card {oid} name', 'before': name, 'after': 'Mutated Card Name'}


def m_broken_link(site, oid, ids):
    p = page(site, oid); t = p.read_text(encoding='utf-8')
    href = '/dc-public-realm/does-not-exist-fixture/'
    t = t.replace('</main>', f'<p><a href="{href}">fixture broken link</a></p></main>', 1)
    p.write_text(t, encoding='utf-8')
    return {'target': 'broken internal link', 'before': 0, 'after': t.count(href)}


def m_remove_nav(site, oid, ids):
    p = page(site, oid); t = p.read_text(encoding='utf-8')
    m = find(t, r'<nav class="primary-nav"[^>]*>')
    b, e = element_span(t, m.start()); t = t[:b] + t[e:]
    p.write_text(t, encoding='utf-8')
    return {'target': 'primary nav', 'before': 1, 'after': t.count('class="primary-nav"')}


def m_orphan(site, oid, ids):
    src = page(site, oid); dst = site / 'objects' / 'synthetic-orphan-page' / 'index.html'
    dst.parent.mkdir(parents=True); shutil.copyfile(src, dst)
    return {'target': 'objects/synthetic-orphan-page/index.html', 'before': False, 'after': dst.exists()}


# data mutations edit the overview record before materialization
def d_blank_field(ov):
    ov['location_source_url'] = ''
    return 'location_source_url', lambda o: o.get('location_source_url') == ''


def d_cc_no_license(ov):
    ov.pop('image_license_url', None)
    assert ov.get('image_rights', '').startswith('CC '), 'fixture overview must carry CC rights'
    return 'image_license_url', lambda o: 'image_license_url' not in o


# ---------------------------------------------------------------- matrix
ROWS = [
    # id, kind, mutation, intended step, diagnostic regex (formatted), expected for OBJ-9104
    ('D1', 'site', m_delete_page, 'Verify PUB-001 canonical-data routes', r'missing published object page\(s\).*{slug}', 'INTENDED_REJECT'),
    ('D2', 'site', m_hide_assertion, 'Verify DATA-001 exact rendered assertion reconciliation', r'{oid}/{A04}: canonical object assertion missing', 'UNEXPECTED_ACCEPT'),
    ('D3', 'site', m_wrong_status, 'Verify EPI-001 public status rule contract', r'{oid}/{A04}: computed status does not match', 'UNEXPECTED_ACCEPT'),
    ('D4', 'site', m_dependency_state, 'Verify EPI-002 rendered dependency state', r'{oid}/{A04}/{AE15}: expected dependency state', 'UNEXPECTED_ACCEPT'),
    ('D5', 'site', m_drop_uncertainty, 'Verify EPI-003 ancestry remains explicit', r'{oid}/{AE07}: empty inheritance list lost its uncertainty qualifier', 'UNEXPECTED_ACCEPT'),
    ('D6', 'site', m_break_lineage, 'Verify EPI-004 rendered claim lineage', r'{oid}/{A01}/{AE01}: terminal Unresolved ancestry missing', 'UNEXPECTED_ACCEPT'),
    ('D7a', 'site', m_remove_conflict, 'Verify EPI-005 rendered material conflicts', r'{oid}/{A01}: canonical conflict has no visible warning', 'UNEXPECTED_ACCEPT'),
    ('D7b', 'site', m_move_conflict, 'Verify EPI-005 warning placement', r'{oid}/{A01}: conflict hidden after provenance disclosure', 'UNEXPECTED_ACCEPT'),
    ('D8', 'data', d_blank_field, 'Validate materialized overview records', r'{oid}: missing location_source_url', 'INTENDED_REJECT'),
    ('D8b', 'data', d_cc_no_license, 'Validate materialized image rights', r'{oid}: Creative Commons image missing image_license_url', 'INTENDED_REJECT'),
    ('D9', 'site', m_card_name, 'Verify DATA-002 canonical summary reconciliation', r'{oid}', 'BLOCKED'),
    ('D10', 'site', m_broken_link, 'Verify PUB-004 internal link integrity', r'does-not-exist-fixture', 'INTENDED_REJECT'),
    ('D11', 'site', m_remove_nav, 'Verify PUB-002 navigation contract', r'{slug}', 'INTENDED_REJECT'),
    ('D12', 'site', m_orphan, 'Verify PUB-001 canonical-data routes', r'orphan object page\(s\).*synthetic-orphan-page', 'INTENDED_REJECT'),
]
POSITIVE_EXPECTED = 'INTENDED_REJECT'


def classify(base, mut, intended, regex):
    if intended not in base or intended not in mut:
        return 'BLOCKED', 'intended validator did not execute'
    b, m = base[intended], mut[intended]
    if b['exit'] != 0:
        return 'BLOCKED', 'intended validator already fails on the unmutated baseline'
    if m['exit'] == 0:
        return 'UNEXPECTED_ACCEPT', ''
    return ('INTENDED_REJECT', '') if re.search(regex, m['out']) else ('WRONG_REASON', 'diagnostic did not match')


def delta(base, mut):
    newly = [n for n in mut if base.get(n, {}).get('exit') == 0 and mut[n]['exit'] != 0]
    changed = [n for n in mut if base.get(n, {}).get('exit', 0) != 0 and mut[n]['exit'] != 0 and base[n]['out'] != mut[n]['out']]
    cleared = [n for n in mut if base.get(n, {}).get('exit', 0) != 0 and mut[n]['exit'] == 0]
    return {'newly_failing': newly, 'baseline_failing_changed_diagnostic': changed, 'baseline_failing_now_passing': cleared}


def snippet(out, regex=None, n=300):
    if regex:
        m = re.search(regex, out)
        if m:
            line = out[out.rfind('\n', 0, m.start()) + 1: out.find('\n', m.end()) if out.find('\n', m.end()) > 0 else None]
            return line.strip()[:n]
    lines = [l for l in out.strip().splitlines() if l.strip()]
    return (lines[-1] if lines else '')[:n]


def main(outdir):
    outdir = Path(outdir).resolve(); outdir.mkdir(parents=True, exist_ok=True)
    t0 = time.time(); log = lambda *a: print(f'[{time.time()-t0:6.0f}s]', *a, flush=True)
    before_repo = repo_inventory(outdir)
    steps = ci_steps(); evals = site_steps(steps)

    log('clean three-object reference build')
    clean = workspace('clean'); clean_full = run_steps(clean, steps)
    assert all(r['exit'] == 0 for r in clean_full.values()), 'clean reference build is not green'

    log('generate OBJ-9104 fixture from clean materialized data')
    fx_path, map_path = TMP / 'fixture.json', TMP / 'id-map.json'
    subprocess.run([sys.executable, str(HERE / 'make_fixture.py'), str(clean / 'build' / 'data'), str(fx_path), str(map_path)], check=True)
    fixture = json.loads(fx_path.read_text(encoding='utf-8')); idmap = json.loads(map_path.read_text(encoding='utf-8'))
    inv_a = {v: k for k, v in idmap['assertions'].items()}; inv_e = {v: k for k, v in idmap['evidence'].items()}
    ids9104 = {'A01': 'A-T9104-01', 'A04': 'A-T9104-04', 'AE01': 'AE-T9104-01', 'AE07': 'AE-T9104-07', 'AE15': 'AE-T9104-15'}
    ids0003 = {k: (inv_a.get(v) or inv_e.get(v)) for k, v in ids9104.items()}
    FXNAME = '9999-12-31-900-test-only-obj-9104.json'

    log('unpatched control (existing production builder)')
    unp = workspace('unpatched', [(FXNAME, fixture)]); unp_full = run_steps(unp, steps)
    log('S0 (temp-patched builder)')
    s0 = workspace('s0', [(FXNAME, fixture)], patched=True); s0_full = run_steps(s0, steps)
    s0_real = {p: sha(s0 / 'site' / p) for p in REAL_PAGES}; clean_real = {p: sha(clean / 'site' / p) for p in REAL_PAGES}
    s0_site_base = {n: s0_full[n] for n in (s['name'] for s in evals)}
    clean_site_base = {n: clean_full[n] for n in (s['name'] for s in evals)}
    s0_inventory = sorted(str(p.relative_to(s0 / 'site')) for p in (s0 / 'site').rglob('*') if p.is_file())

    results = {'baseline': {
        'clean_reference': {'passed': sum(r['exit'] == 0 for r in clean_full.values()), 'total': len(clean_full)},
        'unpatched_control': {'passed': sum(r['exit'] == 0 for r in unp_full.values()), 'total': len(unp_full),
                              'publication': {'exit': unp_full['Build publication from materialized database']['exit'],
                                              'diagnostic': snippet(unp_full['Build publication from materialized database']['out'], r'FileNotFoundError.*')}},
        's0': {'passed': sum(r['exit'] == 0 for r in s0_full.values()), 'total': len(s0_full),
               'failing_steps': {n: snippet(r['out']) for n, r in s0_full.items() if r['exit'] != 0},
               'site_files': len(s0_inventory), 'real_pages_identical_to_clean': s0_real == clean_real},
    }, 'rows': []}

    S0_CHECKS = [
        ('S0a-unpatched', 'Build publication from materialized database', unp_full, 'BLOCKED'),
        ('S0a-patched', 'Build publication from materialized database', s0_full, 'PASS'),
        ('S0b', 'Validate materialized overview records', s0_full, 'PASS'),
        ('S0c', 'Validate overview data', s0_full, 'PASS'),
        ('S0d', 'Verify DATA-002 canonical summary reconciliation', s0_full, 'BLOCKED'),
        ('S0e', 'Verify PUB-001 canonical-data routes|Verify PUB-002 navigation contract|Verify PUB-003 research-task reconciliation|Verify PUB-004 internal link integrity|Verify publication status consistency|Verify final JS-Python object-page parity', s0_full, 'PASS'),
        ('S0f', 'Verify EPI-004 San Martin Daumas-Dumont conflict|Inventory EPI-005 canonical material conflicts|Validate rendered object overviews', s0_full, 'PASS'),
        ('S0g', 'Build and verify JS object-page driver|Verify AUD-10 JS status rule against frozen materialized oracle', s0_full, 'BLOCKED'),
    ]
    for rid, names, res, expected in S0_CHECKS:
        exits = {n: res[n]['exit'] for n in names.split('|')}
        code = 'PASS' if all(v == 0 for v in exits.values()) else 'BLOCKED'
        results['rows'].append({'id': rid, 'kind': 'baseline', 'intended': names.split('|'), 'expected': expected, 'computed': code,
                                'discrepancy': code != expected, 'exits': exits,
                                'diagnostics': {n: snippet(res[n]['out']) for n in exits if exits[n] != 0}})

    for rid, kind, mut, intended, regex_t, expected in ROWS:
        for side, oid, ids in (('OBJ-9104', NEW, ids9104), ('positive-control OBJ-0003', ORIG, ids0003)):
            regex = regex_t.format(oid=oid, slug=SLUG[oid], **ids)
            log(f'{rid} {side}')
            if kind == 'site':
                base_ws, base_res = (s0, s0_site_base) if oid == NEW else (clean, clean_site_base)
                ws = clone(base_ws, f'{rid}-{oid}')
                surface = mut(ws / 'site', oid, ids)
                res = run_steps(ws, evals)
            else:
                tx_list = []
                if oid == NEW:
                    fx = json.loads(json.dumps(fixture))
                    ov = next(o for o in fx['operations'] if o['table'] == 'object_overviews')['value']
                    field, probe = mut(ov); tx_list = [(FXNAME, fx)]; patched = True; base_res = s0_full
                else:
                    ov = json.loads(json.dumps(next(o for o in json.loads((clean / 'build' / 'data' / 'object-overviews.json').read_text())['object_overviews'] if o['object_entity_id'] == ORIG)))
                    field, probe = mut(ov)
                    tx_list = [('9999-12-31-901-test-only-positive-control.json', {
                        'transaction_id': 'TX-TEST-POSITIVE-CONTROL', 'recorded_at': '9999-12-31', 'actor': 'test-fixture',
                        'purpose': 'TEST-ONLY positive control', 'evidence_decision': 'Synthetic.', 'supersedes': None,
                        'operations': [{'table': 'object_overviews', 'action': 'update', 'id': ORIG, 'value': ov}]})]
                    patched = False; base_res = clean_full
                ws = workspace(f'{rid}-{oid}', tx_list, patched=patched)
                res = run_steps(ws, steps)
                mat = ws / 'build' / 'data' / 'object-overviews.json'
                rec = next((o for o in json.loads(mat.read_text())['object_overviews'] if o['object_entity_id'] == oid), None) if mat.exists() else None
                surface = {'target': f'materialized {oid}.{field}', 'before': 'present', 'after': 'mutated' if rec is not None and probe(rec) else 'NOT FOUND IN MATERIALIZED DATA'}
            reached = surface['before'] != surface['after'] and 'NOT FOUND' not in str(surface['after']) and surface['after'] != 'UNCHANGED'
            code, note = classify(base_res, res, intended, regex) if reached else ('BLOCKED', 'mutation did not reach the artifact')
            exp = expected if oid == NEW else POSITIVE_EXPECTED
            real_ok = None
            if oid == NEW and (ws / 'site').exists():
                real_ok = {p: sha(ws / 'site' / p) for p in REAL_PAGES} == s0_real
            results['rows'].append({
                'id': rid, 'side': side, 'kind': kind, 'intended': intended, 'regex': regex, 'surface': surface,
                'mutation_reached_artifact': reached, 'baseline_exit': base_res.get(intended, {}).get('exit'),
                'mutated_exit': res.get(intended, {}).get('exit'), 'computed': code, 'note': note, 'expected': exp,
                'discrepancy': code != exp, 'intended_diagnostic': snippet(res.get(intended, {}).get('out', ''), regex),
                'real_object_pages_unchanged': real_ok, **delta(base_res, res)})
            shutil.rmtree(ws, ignore_errors=True)

    after_repo = repo_inventory(outdir)
    results['real_repository_unchanged'] = before_repo == after_repo
    (outdir / 'results.json').write_text(json.dumps(results, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    (outdir / 's0-inventory.txt').write_text('\n'.join(s0_inventory) + '\n', encoding='utf-8')
    write_markdown(results, outdir / 'results.md')
    log(f"done; real repository unchanged: {results['real_repository_unchanged']}; workspaces in {TMP}")
    shutil.rmtree(TMP, ignore_errors=True)
    assert results['real_repository_unchanged'], 'harness modified the real repository'


def write_markdown(r, path):
    b = r['baseline']
    L = ['# Fourth-object harness results', '',
         f"- Clean reference: {b['clean_reference']['passed']}/{b['clean_reference']['total']} steps pass",
         f"- Unpatched control: {b['unpatched_control']['passed']}/{b['unpatched_control']['total']}; publication exit {b['unpatched_control']['publication']['exit']}: `{b['unpatched_control']['publication']['diagnostic']}`",
         f"- S0 (temp-patched): {b['s0']['passed']}/{b['s0']['total']}; {b['s0']['site_files']} site files; real object pages identical to clean: {b['s0']['real_pages_identical_to_clean']}",
         '- S0 baseline failures (kept separate from row outcomes):'] + \
        [f"  - {n}: `{d}`" for n, d in b['s0']['failing_steps'].items()] + \
        ['', f"Real repository unchanged: {r['real_repository_unchanged']}", '',
         '| Row | Side | Intended validator | Mutation reached | Base exit | Mutated exit | Computed | Expected | Discrepancy | Newly failing elsewhere |',
         '|---|---|---|---|---|---|---|---|---|---|']
    for x in r['rows']:
        if x['kind'] == 'baseline':
            L.append(f"| {x['id']} | baseline | {', '.join(x['intended'])} | — | — | {x['exits']} | {x['computed']} | {x['expected']} | {'**YES**' if x['discrepancy'] else 'no'} | — |")
        else:
            L.append(f"| {x['id']} | {x['side']} | {x['intended']} | {x['mutation_reached_artifact']} | {x['baseline_exit']} | {x['mutated_exit']} | {x['computed']} | {x['expected']} | {'**YES**' if x['discrepancy'] else 'no'} | {', '.join(x['newly_failing']) or '—'} |")
    L += ['', '## Intended-validator diagnostics', '']
    for x in r['rows']:
        if x['kind'] != 'baseline':
            L.append(f"- **{x['id']} / {x['side']}** ({x['computed']}): `{x['intended_diagnostic']}`" + (f" — {x['note']}" if x['note'] else ''))
    path.write_text('\n'.join(L) + '\n', encoding='utf-8')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])
