"""Execute learning notebooks in order; register the internship kernel first."""
import argparse
import json
from pathlib import Path
import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kernel', default='internship')
    args = parser.parse_args()
    results = []
    for path in sorted((ROOT / 'notebooks').glob('[0-9][0-9]_*.ipynb')):
        print(f'Executing {path.name}', flush=True)
        notebook = nbformat.read(path, as_version=4)
        NotebookClient(notebook, timeout=180, kernel_name=args.kernel,
                       resources={'metadata': {'path': str(ROOT)}}).execute()
        nbformat.write(notebook, path)
        results.append({'notebook': path.name, 'code_cells': sum(c.cell_type == 'code' for c in notebook.cells), 'status': 'passed'})
    (ROOT / 'reports' / 'phase7_notebook_audit.json').write_text(json.dumps(results, indent=2) + '\n')
    print(f'{len(results)} notebooks passed.')

if __name__ == '__main__':
    main()
