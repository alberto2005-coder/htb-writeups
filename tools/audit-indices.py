import pathlib, re, sys
from urllib.parse import unquote

ROOT = pathlib.Path('.').resolve()
index_dirs = {'machines', 'machines/starting-point', 'sherlocks', 'challenges', 'knowledge'}

def dirs(pat):
    return {p.parent.as_posix() for p in pathlib.Path('.').glob(pat)}

def split_row(line):
    line = line.strip()
    if line.startswith('|'):
        line = line[1:]
    if line.endswith('|'):
        line = line[:-1]
    return [c.strip() for c in re.split(r'(?<!\\)\|', line)]

def tables(path):
    lines = pathlib.Path(path).read_text(encoding='utf-8').splitlines()
    found, i = [], 0
    while i < len(lines):
        if not lines[i].startswith('|'):
            i += 1
            continue
        j = i
        while j < len(lines) and lines[j].startswith('|'):
            j += 1
        block = lines[i:j]
        if len(block) >= 2 and re.fullmatch(r'\|[\s:|-]+\|', block[1].strip()):
            found.append((split_row(block[0]), block[2:], i + 1))
        i = j
    return found

def root_link_checks(path):
    """Comprueba que el README raíz delegue en los cuatro índices curados."""
    errors = []
    expected = {
        'README.md': {
            'machines/catalog.md', 'challenges/README.md',
            'sherlocks/README.md', 'knowledge/README.md',
        },
        'README.en.md': {
            'machines/catalog.en.md', 'challenges/README.en.md',
            'sherlocks/README.en.md', 'knowledge/README.en.md',
        },
    }[path]
    found = set()
    link_tables = 0
    for header, rows, lineno in tables(path):
        if len(header) != 2 or header[0] not in ('Sección', 'Section'):
            continue
        link_tables += 1
        for k, row in enumerate(rows, lineno + 2):
            cells = split_row(row)
            if len(cells) != 2:
                errors.append(f'{path}:{k}: {len(cells)} columnas en tabla de secciones (esperaba 2)')
                continue
            links = re.findall(r'\]\(([^)]+)\)', row)
            targets = [unquote(l) for l in links if not l.startswith(('http', '#', 'mailto'))]
            if not targets:
                errors.append(f'{path}:{k}: fila de sección sin enlaces: {row[:80]}')
                continue
            for target in targets:
                if target not in expected:
                    continue
                if not (pathlib.Path(path).parent / target).resolve().exists():
                    errors.append(f'{path}:{k}: enlace raíz roto: {target}')
                found.add(target)
    if link_tables != 1:
        errors.append(f'{path}: {link_tables} tablas de secciones (esperaba 1)')
    for target in sorted(expected - found):
        errors.append(f'{path}: falta enlace raíz a {target}')
    return errors, len(found), len(expected)

def resolved(index):
    out = set()
    for link in re.findall(r'\]\(([^)]+)\)', pathlib.Path(index).read_text(encoding='utf-8')):
        if link.startswith(('http', '#', 'mailto')):
            continue
        p = (pathlib.Path(index).parent / unquote(link)).resolve()
        try:
            rel = p.relative_to(ROOT)
        except ValueError:
            continue
        if rel.name in ('README.md', 'README.en.md') and rel.parent.as_posix() not in index_dirs:
            out.add(rel.parent.as_posix())
    return out

machines_all = dirs('machines/*/*/README.md')
machines_retired = {d for d in machines_all if not d.startswith('machines/active/')}
sherlocks_all = {d for d in dirs('sherlocks/*/README.md') if d != 'sherlocks/active' and not d.startswith('sherlocks/active/')}
challenges_all = {d for d in dirs('challenges/*/README.md') if not d.startswith('challenges/active/')}
sp_all = {d for d in machines_all if d.startswith('machines/starting-point/')}

problems = 0
for path, expected in [
    ('machines/catalog.md', machines_retired), ('machines/catalog.en.md', machines_retired),
    ('sherlocks/README.md', sherlocks_all), ('sherlocks/README.en.md', sherlocks_all),
    ('challenges/README.md', challenges_all), ('challenges/README.en.md', challenges_all),
    ('machines/starting-point/README.md', sp_all), ('machines/starting-point/README.en.md', sp_all),
]:
    got = resolved(path)
    problems += len(expected - got) + len(got - expected)
    print(f'{path}: filas={len(got)}/{len(expected)} faltan={len(expected-got)} huerfanas={len(got-expected)}')
    for m in sorted(expected - got)[:5]:
        print('   FALTA', m)

print('root ES:', len(resolved('README.md')), '| root EN:', len(resolved('README.en.md')))

print('\n-- enlaces raíz: índices curados --')
root_errors = []
for path in ('README.md', 'README.en.md'):
    errs, got, total = root_link_checks(path)
    root_errors += errs
    print(f'{path}: enlaces={got}/{total}')
for e in root_errors:
    print('   ERROR', e)
print('enlaces raíz:', 'OK' if not root_errors else f'{len(root_errors)} problemas')
problems += len(root_errors)

# cabeceras de idioma en todos los pares
bad = []
for p in list(pathlib.Path('machines').rglob('README.md')) + \
         list(pathlib.Path('sherlocks').glob('*/README.md')) + \
         list(pathlib.Path('challenges').glob('*/README.md')):
    es = p.read_text(encoding='utf-8').splitlines()[:16]
    en = p.with_name('README.en.md').read_text(encoding='utf-8').splitlines()[:16]
    if not any('README.en.md' in l for l in es):
        bad.append(str(p) + ' (ES sin enlace EN)')
    if not any('README.md' in l for l in en) or any('[🇬🇧 English](README.en.md)' in l for l in en):
        bad.append(str(p.with_name('README.en.md')) + ' (EN mal)')
print('cabeceras de idioma mal:', bad or 'ninguna')
problems += len(bad)

# KB
bad_kb = []
for p in pathlib.Path('knowledge').rglob('*.md'):
    if p.parent == pathlib.Path('knowledge') and p.name in ('README.md', 'README.en.md'):
        continue
    if p.name.endswith('.en.md'):
        continue
    en = p.with_name(p.stem + '.en.md')
    if not en.exists():
        bad_kb.append(f'{p} sin EN')
        continue
    if not any(p.name in l for l in en.read_text(encoding='utf-8').splitlines()[:12]):
        bad_kb.append(f'{en} sin enlace ES')
    if not any(en.name in l for l in p.read_text(encoding='utf-8').splitlines()[:12]):
        bad_kb.append(f'{p} sin enlace EN')
print('KB cabeceras mal:', bad_kb or 'ninguna')
problems += len(bad_kb)

topics = {p.as_posix() for p in pathlib.Path('knowledge').rglob('*.md')
          if not p.name.endswith('.en.md') and p.parent != pathlib.Path('knowledge')}
for idx, target in [('README.md', 'knowledge/README.md'), ('README.en.md', 'knowledge/README.en.md')]:
    links = {unquote(l) for l in re.findall(r'\]\(([^)]+)\)', pathlib.Path(idx).read_text(encoding='utf-8'))}
    if target not in links:
        print(f'{idx}: falta enlace a {target}')
        problems += 1
for idx in ['knowledge/README.md', 'knowledge/README.en.md']:
    got = set()
    for link in re.findall(r'\]\(([^)]+)\)', pathlib.Path(idx).read_text(encoding='utf-8')):
        if link.startswith(('http', '#', 'mailto')):
            continue
        p = (pathlib.Path(idx).parent / unquote(link)).resolve()
        try:
            rel = p.relative_to(ROOT)
        except ValueError:
            continue
        if rel.parts[0] != 'knowledge' or rel.name == 'README.md':
            continue
        if idx.endswith('.en.md'):
            if not rel.name.endswith('.en.md'):
                continue
            rel = rel.with_name(rel.name[:-6] + '.md')
        elif rel.name.endswith('.en.md'):
            continue
        got.add(rel.as_posix())
    print(idx, 'KB:', len(got), '/', len(topics), 'faltan', len(topics-got), 'huerfanos', len(got-topics))
    problems += len(topics-got) + len(got-topics)

# cifras explicitas de estado
pat = re.compile(r'\b(109|209|254)\b[^.\n]{0,40}(ficha|máquina|maquina|recurso|nota|note)|(all|las|los)\s+(109|209)\b', re.I)
print('\n-- cifras de estado sospechosas --')
hits = 0
for p in pathlib.Path('.').rglob('*.md'):
    if ({'.git', '.tmp'} & set(p.parts)) or p.parts[0] == 'private':
        continue
    for i, line in enumerate(p.read_text(encoding='utf-8').splitlines(), 1):
        if pat.search(line):
            hits += 1
            print(f'{p.as_posix()}:{i}: {line.strip()[:130]}')
print('total:', hits)

print('\n-- fechas de actualizacion en indices --')
for p in pathlib.Path('.').glob('README*.md'):
    for i, line in enumerate(p.read_text(encoding='utf-8').splitlines(), 1):
        if re.search(r'[Aa]ctualizad|Last updated|Actualizado', line):
            print(f'{p}:{i}: {line.strip()[:120]}')

print('problemas:', problems)
sys.exit(1 if problems else 0)
