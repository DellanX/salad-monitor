import time
import glob
import threading
import os
from fastapi import FastAPI
import uvicorn

DEFAULT_LOG_DIR = "/logs"

# Version compiled at build time
try:
    from version import VERSION
except Exception:
    VERSION = "unknown"

# Debug mode (compile-time or env override)
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

def debug(msg):
    if DEBUG:
        print(f"[DEBUG] {msg}")

state = {
    "salad_pending": False,
    "salad_active": False,
    "gpu_reserved": False,
    "last_event": None,
    "current_logfile": None,
}

def resolve_log_dir():
    log_dir = os.environ.get("LOG_DIR", DEFAULT_LOG_DIR)
    debug(f"Resolved log_dir = {log_dir}")
    return log_dir

def get_latest_log_file():
    log_dir = resolve_log_dir()
    files = sorted(glob.glob(os.path.join(log_dir, "log-*.txt")))
    debug(f"Files found in {log_dir}: {files}")
    return files[-1] if files else None

def tail_file(path):
    debug(f"Starting to tail file: {path}")
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue
            debug(f"TAIL: {line.strip()}")
            yield line

def parse_line(line: str):
    lower = line.lower()
    debug(f"Parsing line: {line.strip()}")

    if "workload received" in lower or "planned actions" in lower or "requestinstall" in lower:
        state["salad_pending"] = True
        state["last_event"] = "pending"
        debug("EVENT: pending")

    if "gpu hardwarecompatibility" in lower:
        state["gpu_reserved"] = True
        state["last_event"] = "gpu_reserved"
        debug("EVENT: gpu_reserved")

    if "is already running" in lower or "starting workload" in lower:
        state["salad_active"] = True
        state["last_event"] = "active"
        debug("EVENT: active")

    if "workload completed" in lower or "releasing gpu" in lower:
        state["salad_active"] = False
        state["gpu_reserved"] = False
        state["salad_pending"] = False
        state["last_event"] = "idle"
        debug("EVENT: idle")

def monitor_logs():
    last_file = None
    log_dir = resolve_log_dir()
    debug(f"Monitor thread watching directory: {log_dir}")

    while True:
        latest = get_latest_log_file()

        if not latest:
            debug("No log files found. Sleeping...")
            time.sleep(5)
            continue

        debug(f"Latest logfile detected: {latest}")

        if latest != last_file:
            debug(f"Switching logfile from {last_file} to {latest}")
            last_file = latest
            state["current_logfile"] = latest

            for line in tail_file(latest):
                parse_line(line)

app = FastAPI()

@app.get("/gpu-status")
def gpu_status():
    return state

@app.get("/current-logfile")
def current_logfile():
    return {"current_logfile": state["current_logfile"]}

@app.get("/current-logfile-contents")
def current_logfile_contents(lines: int | None = None):
    logfile = state["current_logfile"]
    if not logfile or not os.path.exists(logfile):
        return {"error": "No logfile available"}

    with open(logfile, "r", encoding="utf-8", errors="ignore") as f:
        if lines is None:
            content = f.readlines()
        else:
            content = f.readlines()[-lines:]

    return {"logfile": logfile, "lines": content}

@app.get("/logs")
def list_logs():
    log_dir = resolve_log_dir()
    files = sorted(glob.glob(os.path.join(log_dir, "log-*.txt")))
    return {"log_dir": log_dir, "files": files}

@app.get("/tail")
def tail_raw(lines: int = 50):
    logfile = state["current_logfile"]
    if not logfile or not os.path.exists(logfile):
        return {"error": "No logfile available"}

    with open(logfile, "r", encoding="utf-8", errors="ignore") as f:
        raw = f.readlines()[-lines:]
    return {"logfile": logfile, "lines": raw}

@app.get("/version")
def version():
    return {"version": VERSION}

@app.get("/debug")
def debug_status():
    return {"debug": DEBUG}

@app.get("/health")
def health():
    return {
        "monitor_running": True,
        "current_logfile": state["current_logfile"],
        "log_dir": resolve_log_dir(),
        "version": VERSION,
        "debug": DEBUG,
        "state": state
    }

@app.on_event("startup")
def start_monitor():
    log_dir = resolve_log_dir()
    debug(f"[startup] Launching monitor thread for directory: {log_dir}")
    threading.Thread(target=monitor_logs, daemon=True).start()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

