import json
from pathlib import Path

root = Path.cwd()
examples = root / 'Ejemplos profesor'
print('NOTEBOOKS:')
for nb in sorted(examples.glob('*.ipynb')):
    try:
        data = json.loads(nb.read_text(encoding='utf-8'))
    except Exception as e:
        print('ERR', nb.name, e)
        continue
    print(f'--- {nb.name} ---')
    headings = []
    imports = []
    for cell in data.get('cells', []):
        src = ''.join(cell.get('source', []))
        if not src:
            continue
        text = ' '.join(src.strip().split())
        if cell.get('cell_type') == 'markdown':
            if len(text) < 220:
                headings.append(text[:180])
        if cell.get('cell_type') == 'code':
            if 'import ' in src or 'from ' in src:
                imports.append(src[:200])
    for h in headings[:5]:
        print(h)
    if imports:
        print('IMPORTS:', imports[:3])
    print()

pdf = root / 'docs' / 'pauta' / 'EP2_ISY0101_estudiante.pdf'
print('PDF_EXISTS', pdf.exists())
if pdf.exists():
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(pdf))
        text = ''
        for page in reader.pages[:5]:
            t = page.extract_text() or ''
            text += '\n' + t
        print('PDF_PREVIEW:')
        print(text[:3000])
    except Exception as e:
        print('PDF_ERROR', e)
