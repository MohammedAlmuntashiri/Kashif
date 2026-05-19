"""
scheduler.py — Long-running process that refreshes prices + valuations +
comparisons every 10 minutes during Saudi market hours.

Trading window:  Sunday-Thursday, 10:00-15:00 Asia/Riyadh.
Fire policy:     once when the minute hits a 10-min boundary (00, 10, 20, …)
                 — never twice in the same minute, never outside market hours.

Each cycle runs three scripts via subprocess so each gets its own clean
Flask app context (matches how they're run manually too).
"""
import subprocess
import time
from datetime import datetime
from zoneinfo import ZoneInfo

RIYADH        = ZoneInfo("Asia/Riyadh")
TRADING_DAYS  = {6, 0, 1, 2, 3}     # Sun=6, Mon=0 … Thu=3 (Python weekday())
OPEN_HOUR     = 10
CLOSE_HOUR    = 15                  # exclusive upper bound (last fire at 14:50)
INTERVAL_MIN  = 10
PIPELINE      = ["update_prices.py", "run_valuations.py", "run_comparisons.py"]


def is_market_open(now):
    if now.weekday() not in TRADING_DAYS:
        return False
    return OPEN_HOUR <= now.hour < CLOSE_HOUR


def run_pipeline():
    started = time.time()
    stamp = datetime.now(RIYADH).strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{stamp}] ── pipeline tick ──", flush=True)
    for script in PIPELINE:
        result = subprocess.run(
            ["python", script],
            capture_output=True, text=True, cwd="/app",
        )
        tag = "OK" if result.returncode == 0 else "FAIL"
        last = (result.stdout.strip().splitlines() or [""])[-1]
        print(f"  {tag}  {script:<25} {last}", flush=True)
        if result.returncode != 0:
            # Surface the tail of stderr so the docker logs show what broke.
            print(result.stderr[-500:], flush=True)
    print(f"  done in {time.time() - started:.1f}s", flush=True)


def main():
    print(
        f"Scheduler running — every {INTERVAL_MIN} min, "
        f"{OPEN_HOUR:02d}:00–{CLOSE_HOUR:02d}:00 Asia/Riyadh, "
        f"Sun–Thu.",
        flush=True,
    )
    last_run_minute = -1
    while True:
        now = datetime.now(RIYADH)
        on_boundary = (now.minute % INTERVAL_MIN == 0)
        if is_market_open(now) and on_boundary and now.minute != last_run_minute:
            last_run_minute = now.minute
            try:
                run_pipeline()
            except Exception as e:
                print(f"  pipeline crashed: {type(e).__name__}: {e}", flush=True)
        # 30 s poll is fine — boundaries are 10 min apart and we record the
        # minute we last fired on, so we can't double-fire within the same minute.
        time.sleep(30)


if __name__ == "__main__":
    main()
