from __future__ import annotations

import os
import subprocess
from datetime import datetime

from PySide6.QtCore import QThread, QTimer, Qt, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QPushButton, QProgressBar, QVBoxLayout, QWidget

from core.local_agent import LocalAgent
from vision.screen import capture_jpeg


STYLE = """
QMainWindow,QWidget { background:#070a10; color:#e7edf7; font-family:'Segoe UI'; }
QFrame#panel { background:#0c111a; border:1px solid #1b2636; border-radius:18px; }
QFrame#card { background:#0e141f; border:1px solid #1c2939; border-radius:14px; }
QLabel#brand { font-size:28px; font-weight:800; letter-spacing:3px; }
QLabel#muted { color:#728198; font-size:11px; letter-spacing:1px; }
QLabel#section { color:#8e9bb0; font-size:10px; font-weight:700; letter-spacing:2px; }
QLabel#value { font-size:14px; font-weight:700; }
QLineEdit { background:#0d131d; border:1px solid #27364b; border-radius:14px; padding:14px 16px; color:#f4f7fb; font-size:14px; }
QLineEdit:focus { border:1px solid #4c8dff; }
QPushButton { border:0; border-radius:12px; padding:12px 18px; font-weight:700; }
QPushButton#run { background:#2f7cff; color:white; }
QPushButton#run:hover { background:#4b91ff; }
QPushButton#stop { background:#35151d; color:#ff8d9b; }
QPushButton#chip { background:#121b28; color:#9fb0c8; border:1px solid #223249; }
QProgressBar { background:#111925; border:0; border-radius:5px; height:7px; }
QProgressBar::chunk { background:#3c86ff; border-radius:5px; }
"""


class Worker(QThread):
    status = Signal(str)
    finished = Signal(str)

    def __init__(self, agent: LocalAgent, goal: str):
        super().__init__()
        self.agent, self.goal = agent, goal

    def run(self):
        try:
            result = self.agent.run(self.goal)
            self.finished.emit(result)
        except Exception as exc:
            self.finished.emit(f"Failed: {exc}")


class JarvisWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("J.A.R.V.I.S — Autonomous PC Agent")
        self.resize(1440, 900)
        self.setMinimumSize(1180, 760)
        self.setStyleSheet(STYLE)
        self.agent = LocalAgent(self.log_event)
        self.worker = None
        self._build()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_screen)
        self.timer.start(650)
        self.refresh_screen()
        self.log_event("System initialized • local control ready")

    def _label(self, text, obj="muted"):
        w = QLabel(text); w.setObjectName(obj); return w

    def _card(self, title, value, dot=True):
        c = QFrame(); c.setObjectName("card"); l = QVBoxLayout(c); l.setContentsMargins(15,12,15,12)
        l.addWidget(self._label(title.upper(), "section")); row=QHBoxLayout();
        if dot:
            d=self._label("●", "value"); d.setStyleSheet("color:#38d996; font-size:12px;"); row.addWidget(d)
        v=self._label(value, "value"); row.addWidget(v); row.addStretch(); l.addLayout(row); return c

    def _build(self):
        root=QWidget(); self.setCentralWidget(root); outer=QHBoxLayout(root); outer.setContentsMargins(22,20,22,20); outer.setSpacing(18)
        # sidebar
        side=QFrame(); side.setObjectName("panel"); side.setFixedWidth(260); sl=QVBoxLayout(side); sl.setContentsMargins(22,24,22,22); sl.setSpacing(14)
        sl.addWidget(self._label("J.A.R.V.I.S", "brand")); sl.addWidget(self._label("AUTONOMOUS PC AGENT", "muted")); sl.addSpacing(22)
        for text in ("◉  Command Center","◌  Tasks","◌  Activity","◌  Diagnostics"):
            b=QPushButton(text); b.setObjectName("chip"); b.setCursor(Qt.PointingHandCursor); sl.addWidget(b)
        sl.addStretch(); sl.addWidget(self._label("LOCAL MODE", "section")); sl.addWidget(self._label("NO API KEY REQUIRED", "value")); sl.addWidget(self._label("Ollama vision • Windows executor", "muted")); outer.addWidget(side)
        # main
        main=QVBoxLayout(); main.setSpacing(16); outer.addLayout(main,1)
        head=QHBoxLayout(); title=QVBoxLayout(); title.addWidget(self._label("COMMAND CENTER","section")); title.addWidget(self._label("Ready when you are.","brand")); head.addLayout(title); head.addStretch(); self.clock=self._label("", "muted"); head.addWidget(self.clock,0,Qt.AlignTop); main.addLayout(head)
        body=QHBoxLayout(); body.setSpacing(16); main.addLayout(body,1)
        left=QVBoxLayout(); left.setSpacing(16); body.addLayout(left,1)
        screen=QFrame(); screen.setObjectName("panel"); sv=QVBoxLayout(screen); sv.setContentsMargins(16,16,16,16); sv.addWidget(self._label("LIVE DESKTOP", "section")); self.preview=QLabel(); self.preview.setAlignment(Qt.AlignCenter); self.preview.setMinimumHeight(430); self.preview.setStyleSheet("background:#05070b;border-radius:12px;"); sv.addWidget(self.preview,1); left.addWidget(screen,1)
        cmd=QFrame(); cmd.setObjectName("panel"); cv=QHBoxLayout(cmd); cv.setContentsMargins(12,12,12,12); self.input=QLineEdit(); self.input.setPlaceholderText("Tell JARVIS what to do…  e.g. Open Chrome and create a folder called Projects"); self.input.returnPressed.connect(self.run_goal); cv.addWidget(self.input,1); run=QPushButton("EXECUTE"); run.setObjectName("run"); run.clicked.connect(self.run_goal); cv.addWidget(run); stop=QPushButton("STOP"); stop.setObjectName("stop"); stop.clicked.connect(self.stop); cv.addWidget(stop); left.addWidget(cmd)
        right=QVBoxLayout(); right.setSpacing(12); body.addLayout(right); right.addWidget(self._card("Brain","LOCAL VISION")); right.addWidget(self._card("Vision","LIVE SCREEN")); right.addWidget(self._card("Executor","ONLINE")); right.addWidget(self._card("Safety","GUARDED"))
        task=QFrame(); task.setObjectName("panel"); tv=QVBoxLayout(task); tv.setContentsMargins(18,18,18,18); tv.addWidget(self._label("CURRENT TASK","section")); self.task_label=self._label("IDLE","value"); tv.addWidget(self.task_label); self.progress=QProgressBar(); self.progress.setRange(0,100); self.progress.setValue(0); tv.addWidget(self.progress); right.addWidget(task,1)
        feed=QFrame(); feed.setObjectName("panel"); fv=QVBoxLayout(feed); fv.setContentsMargins(18,18,18,18); fv.addWidget(self._label("ACTIVITY STREAM","section")); self.feed=self._label("System ready.","muted"); self.feed.setWordWrap(True); fv.addWidget(self.feed,1); right.addWidget(feed,2)

    def log_event(self, text):
        now=datetime.now().strftime("%H:%M:%S")
        self.feed.setText((self.feed.text()+f"\n{now}  •  {text}")[-6000:])

    def refresh_screen(self):
        self.clock.setText(datetime.now().strftime("%H:%M:%S  •  %d %b %Y"))
        try:
            data=capture_jpeg(max_width=1100,quality=60); img=QImage.fromData(data); pix=QPixmap.fromImage(img)
            self.preview.setPixmap(pix.scaled(self.preview.size(),Qt.KeepAspectRatio,Qt.SmoothTransformation))
        except Exception as exc: self.preview.setText(f"Screen capture unavailable\n{exc}")

    def run_goal(self):
        goal=self.input.text().strip()
        if not goal or (self.worker and self.worker.isRunning()): return
        self.input.clear(); self.task_label.setText(goal); self.progress.setRange(0,0); self.log_event(f"Planning • {goal}")
        self.worker=Worker(self.agent,goal); self.worker.finished.connect(self.done); self.worker.start()

    def done(self,result):
        self.progress.setRange(0,100); self.progress.setValue(100); self.log_event(result); self.task_label.setText("COMPLETE • "+result[:110]); self.worker=None

    def stop(self):
        self.agent.stop(); self.log_event("Emergency stop • input and mouse released"); self.progress.setRange(0,100); self.progress.setValue(0); self.task_label.setText("STOPPED")

    def closeEvent(self,event):
        self.agent.stop(); event.accept()


def launch():
    app=QApplication.instance() or QApplication([]); app.setApplicationName("J.A.R.V.I.S"); w=JarvisWindow(); w.show(); app.exec()
