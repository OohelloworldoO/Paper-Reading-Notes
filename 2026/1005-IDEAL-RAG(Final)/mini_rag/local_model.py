"""模型連線工具：此檔負責啟動和呼叫模型，不負責檢索或決定答案。

沿用先前下載的 llama.cpp 與 Qwen2.5-1.5B，不需要付費 API。
每次 generate 建立新對話並在結束後停止自己啟動的程序。
"""
from contextlib import contextmanager
from pathlib import Path
import json
import subprocess
import time
import urllib.request

ROOT = Path(__file__).resolve().parent
RUNTIME = ROOT.parents[1] / "work" / "rag-runtime"
URL = "http://127.0.0.1:8091"
ALIAS = "mini-rag-qwen"


def get_json(url):
    with urllib.request.urlopen(url, timeout=2) as response:
        return json.load(response)


@contextmanager
def server():
    def ready():
        try:
            return get_json(URL + "/health").get("status") == "ok"
        except (OSError, ValueError):
            return False

    process = None
    log = None
    try:
        if not ready():
            executable = RUNTIME / "llama" / "llama-server.exe"
            model = RUNTIME / "model.gguf"
            if not executable.is_file() or not model.is_file():
                raise FileNotFoundError(f"找不到已下載模型，請確認路徑：{RUNTIME}")
            (ROOT / "logs").mkdir(exist_ok=True)
            log = (ROOT / "logs" / "server.log").open("a", encoding="utf-8")
            print("正在啟動本機模型，通常需要數秒……", flush=True)
            process = subprocess.Popen(
                [str(executable), "-m", str(model), "--host", "127.0.0.1",
                 "--port", "8091", "-c", "2048", "-t", "6", "-ngl", "0", "--alias", ALIAS],
                stdout=log, stderr=log,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            deadline = time.monotonic() + 60
            while not ready():
                if process.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError("模型啟動失敗，請查看 logs/server.log。")
                time.sleep(0.3)
        models = get_json(URL + "/v1/models")
        if not any(model["id"] == ALIAS for model in models["data"]):
            raise RuntimeError("8091 連接埠上不是本教學模型，請先確認該服務。")
        yield
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=10)
        if log is not None:
            log.close()


def generate(messages):
    body = {"model": ALIAS, "messages": messages,
            "temperature": 0, "seed": 42, "max_tokens": 160}
    request = urllib.request.Request(
        URL + "/v1/chat/completions",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with server():
        with urllib.request.urlopen(request, timeout=180) as response:
            result = json.load(response)
    (ROOT / "logs").mkdir(exist_ok=True)
    stamp = time.time_ns()
    (ROOT / "logs" / f"call-{stamp}.json").write_text(
        json.dumps({"request": body, "response": result}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    choice = result["choices"][0]
    if choice.get("finish_reason") != "stop":
        raise RuntimeError("模型沒有正常結束回答，請查看 logs/call-*.json。")
    return choice["message"]["content"]
