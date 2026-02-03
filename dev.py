import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class RestartHandler(FileSystemEventHandler):
    def __init__(self, script):
        self.script = script
        self.process = None
        self.restart()

    def restart(self):
        if self.process:
            self.process.kill()
        print(f"Reiniciando {self.script}...")
        self.process = subprocess.Popen([sys.executable, self.script])

    def on_modified(self, event):
        if event.src_path.endswith((".py", ".pyw")):
            self.restart()


if __name__ == "__main__":
    script_to_run = "main.pyw"
    event_handler = RestartHandler(script_to_run)
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
