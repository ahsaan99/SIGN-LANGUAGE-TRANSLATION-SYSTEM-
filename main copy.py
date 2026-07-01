import cv2
import mediapipe as mp
import tkinter as tk
from tkinter import ttk
import threading
import time
from PIL import Image, ImageTk
from collections import deque
import pyttsx3




# ── MediaPipe setup ──────────────────────────────────────────────
mp_hands = mp.solutions.hands
mp_draw  = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles




# ── Gesture recognition ──────────────────────────────────────────

def fingers_up(lm, w, h):
    """Return list [thumb, index, middle, ring, pinky] — 1 if finger is up."""
    tips  = [4, 8, 12, 16, 20]   # fingertip landmark IDs
    dip   = [3, 7, 11, 15, 19]   # joint below tip

    pts = {i: (int(lm[i].x * w), int(lm[i].y * h)) for i in range(21)}

    up = []

    # Thumb: compare x-axis (horizontal spread)
    thumb_up = pts[tips[0]][0] < pts[dip[0]][0]   # right hand logic
    up.append(1 if thumb_up else 0)

    # Other four fingers: tip y < pip y  →  finger is up
    for i in range(1, 5):
        up.append(1 if pts[tips[i]][1] < pts[dip[i]][1] else 0)

    return up, pts




def classify_gesture(lm, w, h):
    """Map landmark positions to a gesture label."""
    up, pts = fingers_up(lm, w, h)
    total_up = sum(up)

    # ── Open Palm  →  Hello ──────────────────────────────────────
    if total_up == 5:
        return "Hello", "Open palm"

    # ── Fist  →  No ──────────────────────────────────────────────
    if total_up == 0:
        return "No", "Fist"

    # ── Thumbs Up  →  Yes ────────────────────────────────────────
    if up == [1, 0, 0, 0, 0]:
        return "Yes", "Thumbs up"

    # ── Victory / Peace  →  Thank You ────────────────────────────
    if up == [0, 1, 1, 0, 0]:
        return "Thank You", "Victory sign"

    # ── Raised Hand (4 fingers, no thumb)  →  Help ───────────────
    if up == [0, 1, 1, 1, 1]:
        return "Help", "Raised hand"

    return None, None


# ── Colour palette ───────────────────────────────────────────────
BG        = "#0D1117"
PANEL     = "#161B22"
BORDER    = "#30363D"
ACCENT    = "#1D9E75"
ACCENT_LT = "#E1F5EE"
TEXT_PRI  = "#E6EDF3"
TEXT_SEC  = "#8B949E"
BADGE_BG  = "#1D2D1E"
BTN_HOVER = "#21262D"

GESTURE_COLORS = {
    "Hello":    "#5DCAA5",
    "Yes":      "#7B8FE0",
    "No":       "#E05D5D",
    "Thank You":"#E0A85D",
    "Help":     "#C07BE0",
}

GESTURE_EMOJI = {
    "Hello":    "🖐",
    "Yes":      "👍",
    "No":       "✊",
    "Thank You":"✌️",
    "Help":     "🤚",
}

GESTURE_HOTKEYS = {
    "Hello":    "1",
    "Yes":      "2",
    "No":       "3",
    "Thank You":"4",
    "Help":     "5",
}


# ── Main Application ─────────────────────────────────────────────

class SignLanguageApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sign Language Recognition")
        self.root.configure(bg=BG)
        self.root.minsize(1060, 680)

        # State
        self.running      = True
        self.paused       = False
        self.cap          = None
        self.current_text = tk.StringVar(value="")
        self.status_var   = tk.StringVar(value="Starting camera…")
        self.fps_var      = tk.StringVar(value="-- fps")
        self.gesture_var  = tk.StringVar(value="Waiting…")
        self.gesture_type = tk.StringVar(value="")
        self.confidence   = tk.StringVar(value="")
        self.history      = deque(maxlen=8)
        self.sentence     = []
        self.last_gesture = None
        self.gesture_hold = 0
        self.hold_thresh  = 18        # frames before confirming gesture
        self._fps_times   = deque(maxlen=30)
        # Voice
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 150)
        self.engine.setProperty("volume", 1.0)

        self.last_spoken = ""

        # MediaPipe
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.6,
        )

        self._build_ui()
        self._start_camera()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()
    
    
 #-------- Live speak -------------

    def _speak(self, text):
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print("Speech Error:", e)


    def _update_frame(self, imgtk):
        self.cam_label.imgtk = imgtk
        self.cam_label.configure(image=imgtk)
    

    # ── UI construction ──────────────────────────────────────────

    def _build_ui(self):
        self.root.columnconfigure(0, weight=3)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=0)

        self._build_header()
        self._build_camera_panel()
        self._build_side_panel()
        self._build_footer()


    def _build_header(self):
        hdr = tk.Frame(self.root, bg=PANEL, height=56)
        hdr.grid(row=0, column=0, columnspan=2, sticky="ew")
        hdr.grid_propagate(False)

        # Logo + title
        tk.Label(hdr, text="✋", font=("Arial", 22), bg=PANEL, fg=ACCENT
                 ).pack(side="left", padx=(18, 6), pady=12)
        tk.Label(hdr, text="Sign Language Recognition",
                 font=("Helvetica Neue", 15, "bold"),
                 bg=PANEL, fg=TEXT_PRI).pack(side="left", pady=12)

        # Live badge
        badge = tk.Frame(hdr, bg=BADGE_BG, padx=10, pady=3)
        badge.pack(side="left", padx=16, pady=14)
        self._live_dot = tk.Label(badge, text="●", font=("Arial", 8),
                                   bg=BADGE_BG, fg=ACCENT)
        self._live_dot.pack(side="left", padx=(0, 4))
        tk.Label(badge, text="LIVE", font=("Helvetica Neue", 10, "bold"),
                 bg=BADGE_BG, fg=ACCENT).pack(side="left")
        self._blink_dot()

        # FPS
        tk.Label(hdr, textvariable=self.fps_var, font=("Helvetica Neue", 11),
                 bg=PANEL, fg=TEXT_SEC).pack(side="right", padx=20)
        tk.Label(hdr, text="MediaPipe · 21 landmarks",
                 font=("Helvetica Neue", 11),
                 bg=PANEL, fg=TEXT_SEC).pack(side="right", padx=8)

   
   
    def _blink_dot(self):
        cur = self._live_dot.cget("fg")
        self._live_dot.config(fg=ACCENT if cur == PANEL else PANEL)
        self.root.after(700, self._blink_dot)

    
    
    
    
    
    
    def _build_camera_panel(self):
        container = tk.Frame(self.root, bg=BG, padx=14, pady=14)
        container.grid(row=1, column=0, sticky="nsew")
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        # Camera frame
        cam_outer = tk.Frame(container, bg=BORDER, bd=1)
        cam_outer.grid(row=0, column=0, sticky="nsew")
        cam_outer.rowconfigure(0, weight=1)
        cam_outer.columnconfigure(0, weight=1)

        self.cam_label = tk.Label(cam_outer, bg="#000000",
                                   text="Connecting to camera…",
                                   fg=TEXT_SEC, font=("Helvetica Neue", 13))
        self.cam_label.grid(row=0, column=0, sticky="nsew")

        # Gesture overlay bar
        overlay = tk.Frame(cam_outer, bg="#000000")
        overlay.place(relx=0.0, rely=1.0, anchor="sw",
                      relwidth=1.0, y=-0)

        bar = tk.Frame(overlay, bg="#0D1117", padx=16, pady=10)
        bar.pack(fill="x")

        # Current gesture display
        left = tk.Frame(bar, bg="#0D1117")
        left.pack(side="left")

        self.lbl_detected = tk.Label(left, textvariable=self.gesture_var,
                                      font=("Helvetica Neue", 28, "bold"),
                                      bg="#0D1117", fg=ACCENT)
        self.lbl_detected.pack(anchor="w")
        self.lbl_gtype = tk.Label(left, textvariable=self.gesture_type,
                                   font=("Helvetica Neue", 12),
                                   bg="#0D1117", fg=TEXT_SEC)
        self.lbl_gtype.pack(anchor="w")

        # Confidence bar
        right = tk.Frame(bar, bg="#0D1117")
        right.pack(side="right", padx=(0, 8))
        tk.Label(right, text="HOLD PROGRESS", font=("Helvetica Neue", 9),
                 bg="#0D1117", fg=TEXT_SEC).pack(anchor="e")
        self.progress_bar = ttk.Progressbar(right, length=140,
                                              mode="determinate", maximum=100)
        self.progress_bar.pack()
        self._style_progress()

    def _style_progress(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("green.Horizontal.TProgressbar",
                         troughcolor=BORDER, background=ACCENT,
                         thickness=6, borderwidth=0)
        self.progress_bar.config(style="green.Horizontal.TProgressbar")

    def _build_side_panel(self):
        side = tk.Frame(self.root, bg=BG, padx=0, pady=14)
        side.grid(row=1, column=1, sticky="nsew", padx=(0, 14))
        side.columnconfigure(0, weight=1)

        row = 0

        # ── Output text ─────────────────────────────────────────
        self._section(side, row, "📝  Detected text")
        row += 1

        out_card = tk.Frame(side, bg=PANEL, bd=0, padx=12, pady=10)
        out_card.grid(row=row, column=0, sticky="ew", pady=(0, 12))
        out_card.columnconfigure(0, weight=1)
        row += 1

        self.lbl_output = tk.Label(out_card, textvariable=self.current_text,
                                    font=("Helvetica Neue", 20, "bold"),
                                    bg=PANEL, fg=TEXT_PRI, wraplength=240,
                                    justify="left", anchor="w",
                                    width=16, height=2)
        self.lbl_output.grid(row=0, column=0, sticky="w")

        btn_row = tk.Frame(out_card, bg=PANEL)
        btn_row.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        self._btn(btn_row, "⌫  Undo", self._undo_word, side="left")
        self._btn(btn_row, "✕  Clear", self._clear_output, side="right")

        # ── Gestures ─────────────────────────────────────────────
        self._section(side, row, "🤟  Gestures")
        row += 1

        self.gesture_frames = {}
        for gesture, emoji in GESTURE_EMOJI.items():
            color = GESTURE_COLORS[gesture]
            key   = GESTURE_HOTKEYS[gesture]
            f = tk.Frame(side, bg=PANEL, padx=10, pady=8, cursor="hand2")
            f.grid(row=row, column=0, sticky="ew", pady=2)
            f.columnconfigure(1, weight=1)

            tk.Label(f, text=emoji, font=("Arial", 18),
                     bg=PANEL, fg=color).grid(row=0, column=0, padx=(0, 10))

            info = tk.Frame(f, bg=PANEL)
            info.grid(row=0, column=1, sticky="w")
            tk.Label(info, text=gesture, font=("Helvetica Neue", 13, "bold"),
                     bg=PANEL, fg=TEXT_PRI).pack(anchor="w")
            tk.Label(info, text=f"{GESTURE_HOTKEYS[gesture]} · {gesture.lower()}",
                     font=("Helvetica Neue", 10),
                     bg=PANEL, fg=TEXT_SEC).pack(anchor="w")

            ind = tk.Label(f, text="●", font=("Arial", 8),
                           bg=PANEL, fg=PANEL)
            ind.grid(row=0, column=2, padx=6)

            self.gesture_frames[gesture] = (f, ind, color)
            f.bind("<Enter>", lambda e, fr=f: fr.config(bg=BTN_HOVER))
            f.bind("<Leave>", lambda e, fr=f, g=gesture:
                   fr.config(bg=PANEL if self._active_gesture() != g else "#1A2E25"))
            row += 1

        # ── History ───────────────────────────────────────────────
        self._section(side, row, "🕑  Recent detections")
        row += 1

        hist_card = tk.Frame(side, bg=PANEL, padx=12, pady=8)
        hist_card.grid(row=row, column=0, sticky="ew", pady=(0, 12))
        hist_card.columnconfigure(0, weight=1)
        self.hist_inner = hist_card
        self._update_history_ui()

    def _section(self, parent, row, title):
        lbl = tk.Label(parent, text=title, font=("Helvetica Neue", 11, "bold"),
                       bg=BG, fg=TEXT_SEC)
        lbl.grid(row=row, column=0, sticky="w", pady=(6, 4), padx=2)

   
   
   
    def _btn(self, parent, text, cmd, side="left"):
        b = tk.Button(parent, text=text, command=cmd,
                      font=("Helvetica Neue", 11),
                      bg=BTN_HOVER, fg=TEXT_SEC,
                      activebackground=BORDER, activeforeground=TEXT_PRI,
                      relief="flat", padx=10, pady=4, cursor="hand2",
                      bd=0)
        b.pack(side=side, padx=(0, 4))

    def _build_footer(self):
        footer = tk.Frame(self.root, bg=PANEL, height=42)
        footer.grid(row=2, column=0, columnspan=2, sticky="ew")
        footer.grid_propagate(False)

        # Controls
        tk.Button(footer, text="  ⏸  Pause / Resume  ",
                  command=self._toggle_pause,
                  font=("Helvetica Neue", 11), bg=BTN_HOVER, fg=TEXT_PRI,
                  activebackground=BORDER, relief="flat", padx=8, pady=6,
                  bd=0, cursor="hand2"
                  ).pack(side="left", padx=12, pady=5)

        tk.Button(footer, text="  📷  Restart Camera  ",
                  command=self._restart_camera,
                  font=("Helvetica Neue", 11), bg=BTN_HOVER, fg=TEXT_PRI,
                  activebackground=BORDER, relief="flat", padx=8, pady=6,
                  bd=0, cursor="hand2"
                  ).pack(side="left", padx=4, pady=5)

        # Status
        tk.Label(footer, textvariable=self.status_var,
                 font=("Helvetica Neue", 11),
                 bg=PANEL, fg=TEXT_SEC).pack(side="right", padx=20)

        # Hotkey hint
        tk.Label(footer, text="Hold gesture steady for 0.6 s to confirm",
                 font=("Helvetica Neue", 10),
                 bg=PANEL, fg=TEXT_SEC).pack(side="right", padx=6)

    # ── Camera & detection loop ───────────────────────────────────

    def _start_camera(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if not self.cap.isOpened():
            self.status_var.set("⚠ Camera not found")
            return

        self.status_var.set("Camera ready")

        threading.Thread(
            target=self._camera_loop,
            daemon=True
        ).start()

    def _camera_loop(self):
        while self.running:
            if self.paused:
                time.sleep(0.05)
                continue

            ret, frame = self.cap.read()
            if not ret:
                self.status_var.set("⚠  Lost camera feed")
                time.sleep(0.1)
                continue

            # FPS
            now = time.time()
            self._fps_times.append(now)
            if len(self._fps_times) >= 2:
                fps = (len(self._fps_times) - 1) / (self._fps_times[-1] - self._fps_times[0])
                self.fps_var.set(f"{fps:.0f} fps")

            # MediaPipe
            frame = cv2.flip(frame, 1)
            h, w  = frame.shape[:2]
            rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb)

            detected_gesture = None
            detected_type    = None

            if results.multi_hand_landmarks:
                for hand_lm in results.multi_hand_landmarks:
                    # Draw landmarks
                    mp_draw.draw_landmarks(
                        frame, hand_lm,
                        mp_hands.HAND_CONNECTIONS,
                        mp_styles.get_default_hand_landmarks_style(),
                        mp_styles.get_default_hand_connections_style(),
                    )
                    detected_gesture, detected_type = classify_gesture(
                        hand_lm.landmark, w, h)

            # Hold-to-confirm logic
            self._update_gesture(detected_gesture, detected_type)

            # Overlay box on frame
            self._draw_overlay(frame, detected_gesture)

            # Send to Tkinter
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            imgtk = ImageTk.PhotoImage(image=img)

            self.root.after(
                0,
                lambda i=imgtk: self._update_frame(i)
            )
            time.sleep(0.01)
        if self.cap:
            self.cap.release()

    def _draw_overlay(self, frame, gesture):
        """Draw semi-transparent gesture label on the OpenCV frame."""
        if gesture:
            color_hex = GESTURE_COLORS.get(gesture, "#5DCAA5")
            r, g, b = int(color_hex[1:3],16), int(color_hex[3:5],16), int(color_hex[5:7],16)
            overlay = frame.copy()
            cv2.rectangle(overlay, (10, 10), (340, 60), (13, 17, 23), -1)
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
            cv2.putText(frame, gesture, (20, 48),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.3, (r, g, b), 2, cv2.LINE_AA)

        # Corner brackets
        c = (29, 158, 117)
        lw = 2
        size = 24
        h, w = frame.shape[:2]
        for (x, y) in [(8, 8), (w-8, 8), (8, h-8), (w-8, h-8)]:
            sx = 1 if x < w//2 else -1
            sy = 1 if y < h//2 else -1
            cv2.line(frame, (x, y), (x + sx*size, y), c, lw)
            cv2.line(frame, (x, y), (x, y + sy*size), c, lw)

    def _update_gesture(self, gesture, gtype):
        if gesture == self.last_gesture:
            self.gesture_hold += 1
        else:
            self.gesture_hold = 0
            self.last_gesture = gesture

        pct = min(100, int(self.gesture_hold / self.hold_thresh * 100))
        self.progress_bar["value"] = pct

        if gesture:
            self.gesture_var.set(gesture)
            self.gesture_type.set(gtype or "")
            col = GESTURE_COLORS.get(gesture, ACCENT)
            self.lbl_detected.config(fg=col)
            self._highlight_gesture(gesture)
            self.status_var.set(f"Detecting: {gesture}")
        else:
            self.gesture_var.set("No hand detected")
            self.gesture_type.set("")
            self.lbl_detected.config(fg=TEXT_SEC)
            self._highlight_gesture(None)
            self.status_var.set("Show a hand gesture")

        # Confirm after hold
        if self.gesture_hold == self.hold_thresh and gesture:
            self._confirm_gesture(gesture)

   
   
   
   
   
   
   
   
    def _confirm_gesture(self, gesture):
        print("CONFIRMED:", gesture)
        if gesture != self.last_spoken:
            self.last_spoken = gesture

            self.gesture_var.set(f"🔊 {gesture}")

            self._speak(gesture)

        self.gesture_hold = -10

    def _highlight_gesture(self, active):
        for name, (frame, dot, color) in self.gesture_frames.items():
            if name == active:
                frame.config(bg="#1A2E25")
                dot.config(fg=color)
            else:
                frame.config(bg=PANEL)
                dot.config(fg=PANEL)

    def _active_gesture(self):
        for name, (frame, dot, color) in self.gesture_frames.items():
            if dot.cget("fg") != PANEL:
                return name
        return None

   
   
   
   
   
   
   
    def _update_history_ui(self):
        for w in self.hist_inner.winfo_children():
            w.destroy()
        if not self.history:
            tk.Label(self.hist_inner, text="No detections yet",
                     font=("Helvetica Neue", 11), bg=PANEL,
                     fg=TEXT_SEC).pack(anchor="w")
            return
        for ts, gesture, color in self.history:
            row = tk.Frame(self.hist_inner, bg=PANEL)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=ts, font=("Helvetica Neue", 10),
                     bg=PANEL, fg=TEXT_SEC, width=10, anchor="w"
                     ).pack(side="left")
            tk.Label(row, text=GESTURE_EMOJI.get(gesture, ""), font=("Arial", 11),
                     bg=PANEL).pack(side="left", padx=4)
            tk.Label(row, text=gesture, font=("Helvetica Neue", 11, "bold"),
                     bg=PANEL, fg=color).pack(side="left")

    # ── Controls ─────────────────────────────────────────────────

    def _toggle_pause(self):
        self.paused = not self.paused
        self.status_var.set("Paused — click Resume to continue" if self.paused
                            else "Camera resumed")

   
   
   
    def _clear_output(self):
        self.sentence.clear()
        self.current_text.set("")

   
   
   
    def _undo_word(self):
        if self.sentence:
            self.sentence.pop()
            self.current_text.set(" · ".join(self.sentence))

   
   
   
    def _restart_camera(self):
        if self.cap:
            self.cap.release()

        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        self.status_var.set("Camera restarted")
    
    
    
    
    def _on_close(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.root.destroy()


# ── Entry point ───────────────────────────────────────────────────



if __name__ == "__main__":
    SignLanguageApp()