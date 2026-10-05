"""Веб-интерфейс эмулятора оболочки UNIX (GUI в браузере).

Работает без сторонних зависимостей на стандартной библиотеке Python.
Автоматически открывает вкладку в браузере с графическим терминалом.
"""

import getpass
import json
import os
import socket
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from src.emulator import ShellEmulator
from src.vfs import VFS


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}
  body {{
    background: #121214;
    color: #e0e0e0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    padding: 16px;
  }}
  .window {{
    width: 100%;
    max-width: 960px;
    height: 620px;
    background: #1e1e1e;
    border-radius: 10px;
    box-shadow: 0 18px 45px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.1);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }}
  .titlebar {{
    background: #252526;
    height: 38px;
    display: flex;
    align-items: center;
    padding: 0 14px;
    border-bottom: 1px solid #333333;
    user-select: none;
  }}
  .buttons {{
    display: flex;
    gap: 8px;
    margin-right: 14px;
  }}
  .btn {{
    width: 12px;
    height: 12px;
    border-radius: 50%;
    display: inline-block;
  }}
  .btn-close {{ background: #ff5f56; }}
  .btn-min {{ background: #ffbd2e; }}
  .btn-max {{ background: #27c93f; }}
  .title {{
    font-size: 13px;
    font-weight: 500;
    color: #cccccc;
    font-family: "SF Mono", Monaco, Menlo, Consolas, monospace;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    flex-grow: 1;
    text-align: center;
    margin-right: 48px;
  }}
  .terminal-body {{
    flex: 1;
    background: #1e1e1e;
    padding: 14px 18px;
    overflow-y: auto;
    font-family: "SF Mono", Monaco, Menlo, Consolas, "Courier New", monospace;
    font-size: 14px;
    line-height: 1.5;
    color: #00ff66;
    display: flex;
    flex-direction: column;
  }}
  .output-area {{
    white-space: pre-wrap;
    word-break: break-word;
  }}
  .line-prompt {{
    color: #4ec9b0;
    font-weight: bold;
  }}
  .line-cmd {{
    color: #dcdcdc;
  }}
  .line-output {{
    color: #00ff66;
  }}
  .line-error {{
    color: #ff6b6b;
  }}
  .line-motd {{
    color: #569cd6;
    margin-bottom: 8px;
  }}
  .input-row {{
    display: flex;
    align-items: center;
    margin-top: 4px;
  }}
  .prompt-text {{
    color: #4ec9b0;
    font-weight: bold;
    margin-right: 8px;
    white-space: nowrap;
  }}
  #commandInput {{
    flex: 1;
    background: transparent;
    border: none;
    outline: none;
    color: #ffffff;
    font-family: inherit;
    font-size: inherit;
    caret-color: #00ff66;
  }}
  .status-badge {{
    margin-top: 8px;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    background: #333;
    color: #aaa;
    display: inline-block;
  }}
</style>
</head>
<body>
<div class="window">
  <div class="titlebar">
    <div class="buttons">
      <span class="btn btn-close"></span>
      <span class="btn btn-min"></span>
      <span class="btn btn-max"></span>
    </div>
    <div class="title">{title}</div>
  </div>
  <div class="terminal-body" id="termBody">
    <div class="output-area" id="outputArea"></div>
    <div class="input-row" id="inputRow">
      <span class="prompt-text" id="promptText">{prompt}</span>
      <input type="text" id="commandInput" autofocus autocomplete="off" spellcheck="false">
    </div>
  </div>
</div>

<script>
  const outputArea = document.getElementById("outputArea");
  const commandInput = document.getElementById("commandInput");
  const promptText = document.getElementById("promptText");
  const termBody = document.getElementById("termBody");
  const inputRow = document.getElementById("inputRow");

  const history = [];
  let historyIdx = 0;

  function scrollToBottom() {
    termBody.scrollTop = termBody.scrollHeight;
  }

  function appendText(text, className) {
    if (!text) return;
    const div = document.createElement("div");
    if (className) div.className = className;
    div.textContent = text;
    outputArea.appendChild(div);
    scrollToBottom();
  }

  // Загружаем начальный вывод (motd, скрипты)
  const initial = {initial_json};
  initial.forEach(item => {
    appendText(item.text, item.cls);
  });

  commandInput.addEventListener("keydown", async (e) => {
    if (e.key === "Enter") {
      const line = commandInput.value;
      commandInput.value = "";
      if (line.trim().length > 0) {
        history.push(line);
        historyIdx = history.length;
      }
      appendText(promptText.textContent + line, "line-cmd");

      try {
        const resp = await fetch("/api/execute", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({command: line})
        });
        const data = await resp.json();
        if (data.result) {
          const isErr = data.result.includes("ошибка") ||
                        data.result.includes("Ошибка") ||
                        data.result.includes("не найдена") ||
                        data.result.includes("Нет такого");
          appendText(data.result, isErr ? "line-error" : "line-output");
        }
        if (data.prompt) {
          promptText.textContent = data.prompt;
        }
        if (!data.running) {
          inputRow.style.display = "none";
          appendText("[Сессия завершена. Окно эмулятора закрыто]", "status-badge");
        }
      } catch (err) {
        appendText("Ошибка связи с сервером: " + err, "line-error");
      }
      scrollToBottom();
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      if (history.length > 0 && historyIdx > 0) {
        historyIdx--;
        commandInput.value = history[historyIdx];
      }
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      if (historyIdx < history.length - 1) {
        historyIdx++;
        commandInput.value = history[historyIdx];
      } else {
        historyIdx = history.length;
        commandInput.value = "";
      }
    }
  });

  document.addEventListener("click", () => {
    commandInput.focus();
  });
</script>
</body>
</html>
"""


class ShellWebGUI:
    """Веб-интерфейс эмулятора (GUI в браузере)."""

    def __init__(self, vfs_path=None, script_path=None, host="127.0.0.1", port=0):
        self.vfs = VFS()
        self.vfs_path = vfs_path
        self.script_path = script_path
        self._load_vfs()
        self.emulator = ShellEmulator(self.vfs)
        self.host = host
        self.port = port
        self.initial_items = []
        self._init_session()

    def _load_vfs(self):
        """Загружает VFS из JSON или директории."""
        if self.vfs_path is None:
            return
        if self.vfs_path.endswith(".json"):
            self.vfs.load_from_json(self.vfs_path)
        else:
            self.vfs.load_from_directory(self.vfs_path)

    def _get_title(self):
        """Формирует заголовок окна."""
        try:
            username = getpass.getuser()
        except Exception:
            username = "user"
        try:
            hostname = socket.gethostname()
        except Exception:
            hostname = "localhost"
        return f"Эмулятор - [{username}@{hostname}]"

    def _init_session(self):
        """Инициализирует motd и стартовый скрипт."""
        motd = self.vfs.get_motd()
        if motd:
            self.initial_items.append({"text": motd, "cls": "line-motd"})
        if self.script_path:
            try:
                def on_line(text):
                    cls = "line-cmd" if text.startswith("/") or "$" in text else "line-output"
                    self.initial_items.append({"text": text, "cls": cls})
                self.emulator.run_script(self.script_path, output_callback=on_line)
            except FileNotFoundError:
                self.initial_items.append({
                    "text": f"Скрипт не найден: {self.script_path}",
                    "cls": "line-error"
                })

    def run(self):
        """Запускает веб-сервер и открывает браузер."""
        web_gui = self

        class RequestHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                # Подавляем логирование HTTP в консоль
                return

            def do_GET(self):
                if self.path == "/" or self.path.startswith("/?"):
                    html = HTML_TEMPLATE.format(
                        title=web_gui._get_title(),
                        prompt=web_gui.emulator.get_prompt(),
                        initial_json=json.dumps(web_gui.initial_items, ensure_ascii=False)
                    )
                    content = html.encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                else:
                    self.send_response(404)
                    self.end_headers()

            def do_POST(self):
                if self.path == "/api/execute":
                    length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(length).decode("utf-8")
                    try:
                        data = json.loads(body)
                        cmd = data.get("command", "")
                    except Exception:
                        cmd = ""

                    result = web_gui.emulator.execute(cmd)
                    response_data = {
                        "result": result,
                        "prompt": web_gui.emulator.get_prompt(),
                        "running": web_gui.emulator.running,
                    }
                    content = json.dumps(response_data, ensure_ascii=False).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.send_header("Content-Length", str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                else:
                    self.send_response(404)
                    self.end_headers()

        # Ищем свободный порт
        server = None
        for p in [8080, 8081, 8088, 5000, 0]:
            try:
                server = HTTPServer((self.host, p), RequestHandler)
                self.port = server.server_port
                break
            except OSError:
                continue

        if server is None:
            server = HTTPServer((self.host, 0), RequestHandler)
            self.port = server.server_port

        url = f"http://{self.host}:{self.port}"
        print(f"\n========================================================")
        print(f"  [Web GUI] Графический интерфейс запущен: {url}")
        print(f"  [Web GUI] Открываем окно в браузере...")
        print(f"  Для завершения нажмите Ctrl+C в этом терминале.")
        print(f"========================================================\n")

        # Открываем браузер в отдельном потоке
        threading.Timer(0.3, lambda: webbrowser.open(url)).start()

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n[Web GUI] Сервер остановлен.")
        finally:
            server.server_close()
