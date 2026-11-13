"""Windows desktop launcher for PoE Build Notifier, Python standard library only."""
from __future__ import annotations
import os
import queue
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
import launcher_updater as updater

ROOT = Path(__file__).resolve().parent
BG, PANEL, GOLD, TEXT, MUTED = "#0b0e16", "#171c28", "#dfad73", "#f4f0e9", "#aab0bf"


class Launcher:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("PoE Build Notifier • Launcher")
        self.window.geometry("690x490")
        self.window.minsize(580, 390)
        self.window.configure(bg=BG)
        self.events = queue.Queue()
        self.process = None
        self.busy = False
        self.closing = False
        self.status = tk.StringVar(value="Przygotowywanie...")
        self.version = tk.StringVar(value="Wersja lokalna: " + updater.current_version(ROOT))
        head = tk.Frame(self.window, bg=BG)
        head.pack(fill="x", padx=24, pady=(24, 12))
        tk.Label(head, text="✧  PoE Build Notifier", bg=BG, fg=GOLD,
                 font=("Segoe UI", 21, "bold")).pack(anchor="w")
        tk.Label(head, textvariable=self.version, bg=BG, fg=MUTED,
                 font=("Segoe UI", 10)).pack(anchor="w", pady=5)
        tk.Label(self.window, textvariable=self.status, bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 11), padx=14, pady=14, anchor="w").pack(fill="x", padx=24)
        bar = tk.Frame(self.window, bg=BG)
        bar.pack(fill="x", padx=24, pady=13)
        self.start_button = self.button(bar, "▶ Uruchom bota", self.start, GOLD, "#20150c")
        self.stop_button = self.button(bar, "■ Zatrzymaj", self.stop)
        self.update_button = self.button(bar, "↻ Sprawdź aktualizacje", self.check)
        tk.Label(self.window, text="LOGI", bg=BG, fg=GOLD,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=24)
        self.logbox = tk.Text(self.window, bg=PANEL, fg=TEXT, insertbackground=TEXT,
                              relief="flat", font=("Consolas", 9), state="disabled",
                              wrap="word", height=15)
        self.logbox.pack(fill="both", expand=True, padx=24, pady=(8, 20))
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.after(100, self.drain)
        self.check(auto_start=True)

    def button(self, parent, label, command, bg=PANEL, fg=TEXT):
        widget = tk.Button(parent, text=label, command=command, bg=bg, fg=fg,
                           activebackground=GOLD, relief="flat",
                           font=("Segoe UI", 10, "bold"), padx=12, pady=9)
        widget.pack(side="left", padx=(0, 9))
        return widget

    def emit(self, kind, value):
        self.events.put((kind, value))

    def log(self, value):
        self.emit("log", value)

    def check(self, auto_start=False):
        if self.busy or (self.process and self.process.poll() is None):
            return
        self.busy = True
        self.status.set("Sprawdzanie aktualizacji GitHub...")
        self.update_button.configure(state="disabled")
        def work():
            try:
                remote, sha = updater.remote_release()
                local = updater.current_version(ROOT)
                if updater.is_newer(remote, local):
                    self.log("Nowa wersja " + remote + " (lokalnie " + local + ")")
                    self.emit("status", "Pobieranie aktualizacji " + remote + "...")
                    updater.install(ROOT, sha, remote, logger=self.log)
                    self.log("Zainstalowano wersję " + remote)
                    self.emit("version", remote)
                    # This launcher was loaded before the update. Restart through
                    # a newly loaded process to use updated updater/launcher code.
                    self.emit("restart", None)
                    return
                self.log("Wersja aktualna: " + local)
            except Exception as exc:
                self.log("Nie udało się sprawdzić/zainstalować aktualizacji: " + str(exc))
                self.log("Uruchomienie dotychczasowej wersji nadal jest możliwe.")
            finally:
                self.emit("check_done", auto_start)
        threading.Thread(target=work, daemon=True).start()

    def start(self):
        if self.busy or (self.process and self.process.poll() is None):
            return
        self.status.set("Uruchamianie bota...")
        try:
            kwargs = {"cwd": str(ROOT), "stdout": subprocess.PIPE,
                      "stderr": subprocess.STDOUT, "text": True,
                      "encoding": "utf-8", "errors": "replace", "bufsize": 1}
            if os.name == "nt":
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
            self.process = subprocess.Popen([sys.executable, "-u", str(ROOT / "main.py")], **kwargs)
            self.status.set("Bot uruchomiony • PID " + str(self.process.pid))
            threading.Thread(target=self.read_logs, args=(self.process,), daemon=True).start()
        except Exception as exc:
            self.status.set("Błąd uruchomienia")
            self.log(str(exc))

    def read_logs(self, process):
        try:
            for line in process.stdout:
                self.log(line.rstrip())
        finally:
            self.emit("ended", process)

    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.status.set("Zatrzymywanie bota...")

    def close(self):
        self.closing = True
        self.stop()
        self.window.destroy()

    def drain(self):
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "log":
                    self.logbox.configure(state="normal")
                    self.logbox.insert("end", str(value) + "\n")
                    self.logbox.see("end")
                    self.logbox.configure(state="disabled")
                elif kind == "status":
                    self.status.set(value)
                elif kind == "version":
                    self.version.set("Wersja lokalna: " + value)
                elif kind == "restart":
                    self.status.set("Aktualizacja gotowa. Restart launchera...")
                    args = [sys.executable, str(ROOT / "launcher.pyw")]
                    subprocess.Popen(args, cwd=ROOT)
                    self.close()
                    return
                elif kind == "check_done":
                    self.busy = False
                    self.update_button.configure(state="normal")
                    if value and not self.closing:
                        self.start()
                    elif not self.closing:
                        self.status.set("Gotowy")
                elif kind == "ended":
                    if value == self.process:
                        self.status.set("Bot zatrzymany (kod " + str(value.returncode) + ")")
        except queue.Empty:
            pass
        if not self.closing:
            self.window.after(100, self.drain)

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    Launcher().run()
