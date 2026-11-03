"""Reproduce all six phases and numerical checks using saved Yahoo snapshots."""
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
STEPS=['phase1.py','check_phase1.py','phase2.py','check_phase2.py','phase3.py','phase4.py','check_phase4.py','phase5.py','check_phase5.py','phase6.py','check_phase6.py']
if __name__=='__main__':
    for step in STEPS:
        print(f'Running {step}',flush=True)
        subprocess.run([sys.executable,str(ROOT/'src'/step)],cwd=ROOT,check=True)
    print('All phases and available numerical checks completed.')
