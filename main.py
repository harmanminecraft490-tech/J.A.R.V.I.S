from __future__ import annotations

import threading
import tkinter as tk
from tkinter import messagebox, simpledialog

from brain.google_computer_use import GoogleComputerUse
from config.key_store import load_api_key, save_api_key, mask_api_key


class JarvisApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("J.A.R.V.I.S — Computer Use")
        self.root.geometry("1000x680")
        self.root.configure(bg="#080b12")
        self.api_key = load_api_key()
        if not self.api_key:
            self.api_key = simpledialog.askstring("J.A.R.V.I.S Setup", "Enter your Google AI Studio / Gemini API key:", show="*", parent=self.root)
            if not self.api_key:
                raise SystemExit("Google AI API key is required.")
            save_api_key(self.api_key.strip())
        self.agent = GoogleComputerUse(self.api_key, self.status)
        self._build_ui()

    def _build_ui(self) -> None:
        tk.Label(self.root, text="J.A.R.V.I.S", fg="#e7edf7", bg="#080b12", font=("Segoe UI", 28, "bold")).pack(anchor="w", padx=28, pady=(24, 0))
        tk.Label(self.root, text="GOOGLE COMPUTER USE • LIVE DESKTOP CONTROL", fg="#68748a", bg="#080b12", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=30)
        self.log = tk.Text(self.root, bg="#0d111b", fg="#b8c4d8", insertbackground="white", relief="flat", font=("Consolas", 10), state="disabled")
        self.log.pack(fill="both", expand=True, padx=28, pady=20)
        row = tk.Frame(self.root, bg="#080b12"); row.pack(fill="x", padx=28, pady=(0, 24))
        self.entry = tk.Entry(row, bg="#111722", fg="white", insertbackground="white", relief="flat", font=("Segoe UI", 12))
        self.entry.pack(side="left", fill="x", expand=True, ipady=12)
        self.entry.bind("<Return>", lambda _: self.run_goal())
        tk.Button(row, text="EXECUTE", command=self.run_goal, bg="#1d6fff", fg="white", relief="flat", padx=24, pady=10).pack(side="left", padx=(12, 0))
        tk.Button(row, text="STOP", command=lambda: self.status("Emergency stop requested"), bg="#35151b", fg="#ff8795", relief="flat", padx=18, pady=10).pack(side="left", padx=(8, 0))
        self.status("READY • Google AI key: " + mask_api_key(self.api_key))

    def status(self, text: str) -> None:
        self.root.after(0, self._append, text)

    def _append(self, text: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", f"• {text}\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def run_goal(self) -> None:
        goal = self.entry.get().strip()
        if not goal: return
        self.entry.delete(0, "end")
        self.status("OBSERVE → REASON → ACT → VERIFY")
        threading.Thread(target=self._worker, args=(goal,), daemon=True).start()

    def _worker(self, goal: str) -> None:
        try:
            result = self.agent.run(goal)
            self.status("COMPLETE: " + result[:1000])
        except Exception as exc:
            self.status(f"BLOCKED/FAILED: {exc}")

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    JarvisApp().run()
