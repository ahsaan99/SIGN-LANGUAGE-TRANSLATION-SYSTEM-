<div align="center">

```
███████╗██╗ ██████╗ ███╗   ██╗    ██╗      █████╗ ███╗   ██╗ ██████╗ 
██╔════╝██║██╔════╝ ████╗  ██║    ██║     ██╔══██╗████╗  ██║██╔════╝ 
███████╗██║██║  ███╗██╔██╗ ██║    ██║     ███████║██╔██╗ ██║██║  ███╗
╚════██║██║██║   ██║██║╚██╗██║    ██║     ██╔══██║██║╚██╗██║██║   ██║
███████║██║╚██████╔╝██║ ╚████║    ███████╗██║  ██║██║ ╚████║╚██████╔╝
╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝    ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ 
```

# ✋ Sign Language Recognition

### *Real-time hand gesture detection · No training required · Works offline*

<br/>

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10%2B-00897B?style=for-the-badge&logo=google&logoColor=white)](https://mediapipe.dev)
[![Tkinter](https://img.shields.io/badge/Tkinter-UI-FF6F00?style=for-the-badge&logo=python&logoColor=white)](https://docs.python.org/3/library/tkinter.html)
[![License](https://img.shields.io/badge/License-MIT-1D9E75?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Live%20%F0%9F%9F%A2-success?style=for-the-badge)]()

<br/>

> **"The system uses OpenCV and MediaPipe to track 21 hand landmarks, applies custom coordinate-based rules to identify hand gestures, and displays the corresponding text in real time."**

<br/>

---

</div>

<br/>

## 🌟 What Is This?

This project turns your **webcam** into a sign language interpreter. Show a hand gesture to the camera — the app detects **21 precise landmarks** on your hand, runs them through a custom rule engine, and instantly prints the meaning as text on screen.

No neural network. No cloud. No dataset. Just pure computer vision — fast, offline, and explainable.

```
You show a gesture  →  Camera sees it  →  AI finds your hand  →  Text appears instantly
         🖐                  📷                   🧠                       ✅
```

<br/>

---

## 📸 Demo

```
┌─────────────────────────────────────────────────────────┐
│  ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐  │
│                                                          │
│  │                                                 │  │  │
│  │            ●───●───●───●───●                    │  │  │
│  │           /   /   |   \   \                     │  │  │
│  │          ●   ●   |   ●   ●                     │  │  │
│  │         /   /   |   \   \                      │  │  │
│  │        ●   ●   |   ●   ●                      │  │  │
│  │                 ●                              │  │  │
│  │            ┌────┴────┐                         │  │  │
│  │            │  Hello  │  97% confidence         │  │  │
│  │            └─────────┘                         │  │  │
│  │                                                 │  │  │
│  └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘  │
│                  30 fps · MediaPipe · 21 landmarks       │
└─────────────────────────────────────────────────────────┘
```

<br/>

---

## ⚡ Quick Start

### 1 · Clone or download

```bash
git clone https://github.com/yourname/sign-language-recognition.git
cd sign-language-recognition
```

### 2 · Install dependencies

```bash
pip install -r requirements.txt
```

> 🐧 **Linux users only:** `sudo apt install python3-tk`

### 3 · Run

```bash
python sign_language_app.py
```

That's it. The window opens, your camera turns on, and detection starts immediately. ✅

<br/>

---

## 🤟 Supported Gestures

| # | Gesture | Emoji | Displayed Text | How to make it |
|---|---------|-------|----------------|----------------|
| 1 | Open Palm | 🖐 | **Hello** | All 5 fingers fully extended |
| 2 | Thumbs Up | 👍 | **Yes** | Only your thumb pointing up |
| 3 | Fist | ✊ | **No** | All fingers curled tightly in |
| 4 | Victory Sign | ✌️ | **Thank You** | Index + middle fingers up, rest down |
| 5 | Raised Hand | 🤚 | **Help** | Four fingers up, thumb tucked in |

<br/>

---

## 🧠 How It Works — The Full Pipeline

```
 ╔══════════════╗
 ║  YOUR WEBCAM ║
 ╚══════╤═══════╝
        │  Raw video stream (BGR frames)
        ▼
 ╔══════════════════════════╗
 ║  OpenCV Frame Capture    ║  cv2.VideoCapture(0)
 ║  flip · resize · convert ║  cv2.flip(frame, 1)
 ╚══════╤═══════════════════╝
        │  RGB numpy array
        ▼
 ╔══════════════════════════╗
 ║  MediaPipe Hands Model   ║  21 landmark points
 ║  Detection + Tracking    ║  x, y, z per point
 ╚══════╤═══════════════════╝
        │  Normalized (0–1) coordinates
        ▼
 ╔══════════════════════════╗
 ║  Finger State Analyzer   ║  fingers_up() function
 ║  [thumb,idx,mid,rng,pnk] ║  e.g.  [1, 1, 1, 1, 1]
 ╚══════╤═══════════════════╝
        │  Binary finger pattern
        ▼
 ╔══════════════════════════╗
 ║  Gesture Rule Engine     ║  classify_gesture()
 ║  Pattern matching        ║  [0,1,1,0,0] → Thank You
 ╚══════╤═══════════════════╝
        │  Confirmed label (after 0.6 s hold)
        ▼
 ╔══════════════════════════╗
 ║  Tkinter UI Overlay      ║  Text · History · Sidebar
 ║  + OpenCV frame overlay  ║  30 fps real-time display
 ╚══════════════════════════╝
```

<br/>

### 🗺️ The 21 Hand Landmarks

MediaPipe assigns a number (0–20) to every key point on your hand:
<img width="738" height="258" alt="image" src="https://github.com/user-attachments/assets/c5ccdead-a2d6-495f-9a09-df40f2b2d8ac" />

```
                    8   12  16  20
                    |   |   |   |
                    7   11  15  19
              4     |   |   |   |
              |     6   10  14  18
              3     |   |   |   |
              |     5───9───13──17
              2    /
               \  /
         1──────0  ← WRIST
```

| ID | Landmark | ID | Landmark |
|----|----------|----|----------|
| 0 | Wrist | 11 | Middle PIP |
| 1 | Thumb CMC | 12 | Middle DIP |
| 2 | Thumb MCP | 13 | Ring MCP |
| 3 | Thumb IP | 14 | Ring PIP |
| 4 | Thumb Tip | 15 | Ring DIP |
| 5 | Index MCP | 16 | Ring Tip |
| 6 | Index PIP | 17 | Pinky MCP |
| 7 | Index DIP | 18 | Pinky PIP |
| 8 | Index Tip | 19 | Pinky DIP |
| 9 | Middle MCP | 20 | Pinky Tip |
| 10 | Middle PIP | | |

> **Key insight:** A finger is *up* when its **tip y-coordinate < pip y-coordinate** (tip is higher on screen than the knuckle below it).

<br/>

---

## 🎨 UI Layout

```
┌──────────────────────────────────────────────────────────────────┐
│  ✋  Sign Language Recognition          LIVE ●    30 fps         │  ← Header
├────────────────────────────────────┬─────────────────────────────┤
│                                    │  📝 Detected Text           │
│                                    │  ┌─────────────────────┐   │
│        LIVE CAMERA FEED            │  │  Hello · Yes        │   │
│        (640 × 480)                 │  └─────────────────────┘   │
│                                    │  [ ⌫ Undo ]  [ ✕ Clear ]  │
│   ┌ ─ ─ corner brackets ─ ─ ┐     │                             │
│   │                         │     │  🤟 Gestures                │
│   │    hand landmarks        │     │  🖐  Hello       ●         │
│   │    drawn in green        │     │  👍  Yes                   │
│   │                         │     │  ✊  No                     │
│   └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘     │  ✌️  Thank You             │
│                                    │  🤚  Help                   │
│  ┌─────────────────────────────┐   │                             │
│  │  Hello          97%  ████▒  │   │  🕑 Recent Detections      │
│  └─────────────────────────────┘   │  14:03:22  🖐  Hello       │
│             ↑ Overlay bar          │  14:03:18  👍  Yes         │
├────────────────────────────────────┴─────────────────────────────┤
│  [ ⏸ Pause ]  [ 📷 Restart ]    Hold steady 0.6 s to confirm    │  ← Footer
└──────────────────────────────────────────────────────────────────┘
```

<br/>

---

## 🧩 Project Structure

```
sign-language-recognition/
│
├── 📄 sign_language_app.py      ← Main application (run this)
│     ├── SignLanguageApp         UI class + event loop
│     ├── classify_gesture()      Rule engine
│     ├── fingers_up()            Landmark math
│     └── _camera_loop()          Threaded capture
│
├── 📄 requirements.txt          ← pip dependencies
└── 📄 README.md                 ← This file
```

<br/>

---

## ➕ Add Your Own Gesture (2 lines of code)

Open `sign_language_app.py` and find the `classify_gesture()` function. Gestures are defined by a binary list:

```
[thumb, index, middle, ring, pinky]
  1=up   1=up   1=up   1=up  1=up
  0=down 0=down 0=down 0=down 0=down
```

**Example — add "I Love You" (ILY):**

```python
# Thumb up, index up, pinky up → ILY hand
if up == [1, 1, 0, 0, 1]:
    return "I Love You", "ILY sign"
```

Then add it to the dictionaries at the top:

```python
GESTURE_COLORS = { ..., "I Love You": "#E07BB5" }
GESTURE_EMOJI  = { ..., "I Love You": "🤟" }
GESTURE_HOTKEYS = { ..., "I Love You": "6" }
```

Done — it appears automatically in the sidebar. 🎉

<br/>

---

## 🔧 Configuration

Inside `sign_language_app.py`, you can tweak these constants:

| Constant | Default | Effect |
|----------|---------|--------|
| `hold_thresh` | `18` frames | Frames to hold before confirming a gesture (lower = faster, less stable) |
| `min_detection_confidence` | `0.7` | How confident MediaPipe must be before reporting a hand |
| `min_tracking_confidence` | `0.6` | Confidence needed to keep tracking between frames |
| `max_num_hands` | `1` | Increase to `2` for two-hand detection |

<br/>

---

## ✅ Advantages

```
╔═══════════════════════════════╗   ╔═══════════════════════════════╗
║  ✅  No AI training needed    ║   ║  ✅  Works completely offline  ║
║  ✅  No dataset collection    ║   ║  ✅  Runs on any laptop webcam ║
║  ✅  Fast (30 fps)            ║   ║  ✅  Easy to explain + demo    ║
║  ✅  Lightweight (~50 MB)     ║   ║  ✅  Extendable in minutes     ║
╚═══════════════════════════════╝   ╚═══════════════════════════════╝
```

<br/>

---

## 🔮 Future Scope

- [ ] 🔊 **Text-to-speech** — speak the detected word aloud
- [ ] 🔤 **Full alphabet** — support A–Z finger-spelling
- [ ] 🎥 **Dynamic gestures** — recognize movement-based signs (e.g. waving)
- [ ] 📱 **Mobile app** — Android/iOS port via Flutter + TFLite
- [ ] 🌐 **Web version** — run in-browser with MediaPipe JS
- [ ] 🤝 **Two-hand support** — recognize signs that use both hands
- [ ] 🌍 **Multi-language** — map gestures to other spoken languages

<br/>

---

## 🐛 Troubleshooting

<details>
<summary><b>📷 Camera not found / black screen</b></summary>

- Make sure no other app (Zoom, Teams, OBS) is using the webcam
- Click **Restart Camera** in the app footer
- Try changing `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)` if you have multiple cameras

</details>

<details>
<summary><b>🤚 Gestures are misclassified</b></summary>

- Ensure your hand is well-lit from the front
- Keep your hand 30–70 cm from the camera
- Keep a plain, non-cluttered background
- Try lowering `min_detection_confidence` to `0.6`

</details>

<details>
<summary><b>📦 Import error: mediapipe not found</b></summary>

```bash
pip install mediapipe --upgrade
```

If that fails on Python 3.12+:
```bash
pip install mediapipe==0.10.9
```

</details>

<details>
<summary><b>🪟 Tkinter window doesn't open (Linux)</b></summary>

```bash
sudo apt-get install python3-tk
```

</details>

<br/>

---

## 📦 Requirements

```
opencv-python >= 4.8.0     # Camera capture + frame processing
mediapipe    >= 0.10.0     # Hand landmark detection
Pillow       >= 10.0.0     # Frame → Tkinter image conversion
tkinter                    # UI (bundled with Python on Win/macOS)
```

<br/>

---

## 📜 License

```
MIT License — free to use, modify, and distribute.
Just keep the credits intact. ✌️
```

<br/>

---

<div align="center">

### Built with ❤️ using Python · OpenCV · MediaPipe

*Made for school exhibitions, hackathons, and anyone curious about computer vision.*

**⭐ Star this repo if it helped you!**

<br/>

```
  🖐 Hello    👍 Yes    ✊ No    ✌️ Thank You    🤚 Help
```

</div>
