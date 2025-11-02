import os, pandas as pd, datetime as dt

def log_print(msg: str):
    ts = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts} UTC] {msg}", flush=True)

def append_csv(path: str, row: dict):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    df = pd.DataFrame([row])
    exists = os.path.exists(path)
    df.to_csv(path, mode="a", header=not exists, index=False, encoding="utf-8")