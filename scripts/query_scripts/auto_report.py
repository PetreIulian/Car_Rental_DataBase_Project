import sys
import time
from pathlib import Path
import subprocess
from datetime import datetime

RUN_EVERY = 5
CYCLES = 5

SolvePath = Path(__file__).resolve().parent
REPORTS = SolvePath / "reports.py"
OUT_DIR = SolvePath / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

LOG_PATH = SolvePath / "audit.logs"

def log(msg):
    line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {msg}\n" # Am adăugat \n la final
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line)

def main():
    print("AUTO REPORT START")
    print("reports.py:", REPORTS)
    print("outputs:", OUT_DIR)
    for i in range(1, CYCLES +  1):
        log(f"Cycle: {i} started")
        res = subprocess.run(
            [sys.executable, str(REPORTS)],
            cwd=str(SolvePath),
            capture_output=True,
            text=True,
        )

        print(f"\n=== Cycle: {i} ===")
        if res.stdout:
            print(res.stdout)
        if res.stderr:
            print("STDERR: \n", res.stderr)
        if res.returncode != 0:
            log(f"Cycle: {i} FAILED (code={res.returncode})")
            break
        else:
            log(f"Cycle: {i} finished without errors")

        time.sleep(RUN_EVERY)

    print("AUTO REPORT ENDDED")

if __name__ == "__main__":
    main()