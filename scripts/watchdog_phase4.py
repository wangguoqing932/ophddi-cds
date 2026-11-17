#!/usr/bin/env python3
"""Watchdog: monitor LightRAG build and auto-resume if it dies."""
import subprocess, time, json
from pathlib import Path

ROOT = Path(r"C:\Users\Administrator\ZCodeProject\ophthalmic-ddi-cds")
CHECK_INTERVAL = 300  # 5 min

def is_build_running():
    result = subprocess.run(["python", "scripts/build_lightrag_index.py", "--project-root", ".", "--status"],
                          cwd=ROOT, capture_output=True, text=True, timeout=30)
    return "paused" in result.stdout.lower() or "running" in result.stdout.lower()

def resume_build():
    print(f"[watchdog] Build stopped — resuming...")
    subprocess.Popen(["python", "scripts/build_lightrag_index.py", "--project-root", ".", "--resume"],
                    cwd=ROOT)

print("[watchdog] Starting monitor...")
restart_count = 0
while True:
    try:
        if not is_build_running():
            restart_count += 1
            resume_build()
        else:
            # Get current node count
            result = subprocess.run(["grep", "Writing graph", 
                "C:/Users/Administrator/.zcode/cli/exec/sess_5f302698-9920-48b7-b9d2-c97df4d5f7b0/call_00_N1SjUqRuMG99Hx7HrRxm8359-stdout.log"],
                capture_output=True, text=True, timeout=10)
            last = result.stdout.strip().split('\n')[-1] if result.stdout.strip() else "N/A"
            print(f"[watchdog] OK - {last[-60:]}")
    except Exception as e:
        print(f"[watchdog] Error: {e}")
    time.sleep(CHECK_INTERVAL)
