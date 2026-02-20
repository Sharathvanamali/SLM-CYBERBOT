

# 🌆 CyberBot — Neural Code Interface

> Neo-Noir Cyberpunk AI Coding Assistant powered by CodeGemma + Ollama + Streamlit

CyberBot is a visually immersive, cyberpunk-styled AI coding assistant built with **Streamlit** and powered locally by **Ollama** running:

```
hf.co/MaziyarPanahi/codegemma-2b-GGUF:Q4_k_M
```

It delivers structured reasoning, production-ready code generation, debugging analysis, and optional voice input — all inside a futuristic neural interface.

---

## ✨ Features

* ⚡ **Local LLM Execution (Ollama)**
* 🧠 Multiple operation modes:

  * Normal
  * Deep Thought (structured reasoning)
  * Code Master (production-ready code)
  * Debug (root cause analysis + full fix)
* 💻 Beautiful custom code window renderer
* 🎙 Optional voice input (SpeechRecognition)
* 📊 Session metrics panel
* 🔎 Thought process display toggle
* 🧩 Styled Neo-Noir Cyberpunk UI (custom CSS engine)
* 🧵 Streaming token output
* 🧠 Context memory (last 30 exchanges)

---

## 🖼 Interface Preview

> Futuristic neon skyline theme
> Structured response panels
> Neural thought display
> Code blocks with glowing syntax window

---

## 🛠 Tech Stack

* **Frontend/UI**: Streamlit
* **LLM Runtime**: Ollama
* **Model**: CodeGemma 2B GGUF (Q4_k_M)
* **Optional Audio**: SpeechRecognition + PyAudio
* **Language**: Python 3.9+

---

## 📦 Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/yourusername/cyberbot.git
cd cyberbot
```

---

### 2️⃣ Install Python dependencies

```bash
pip install streamlit ollama SpeechRecognition pyaudio
```

> If PyAudio fails on Windows, install wheel from:
> [https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)

---

### 3️⃣ Install & Start Ollama

Install Ollama:

```bash
https://ollama.com/download
```

Start the Ollama server:

```bash
ollama serve
```

---

### 4️⃣ Pull the required model

```bash
ollama pull hf.co/MaziyarPanahi/codegemma-2b-GGUF:Q4_k_M
```

---

### 5️⃣ Run CyberBot

```bash
streamlit run app.py
```

Then open:

```
http://localhost:8501
```

---

## 🧠 Operation Modes

### 🟦 Normal

Standard AI responses.

### 🟪 Deep Thought

Structured reasoning:

* 🔍 Problem Breakdown
* 💡 Approach
* ⚙️ Implementation
* ✅ Test Cases
* 🚀 Optimisations

### 🟢 Code Master

* Production-ready code
* Type hints
* Docstrings
* Error handling
* Edge cases
* Complexity analysis

### 🟡 Debug

* 🐛 Root Cause
* 🔬 Line-by-line Analysis
* 🔧 Full Fixed File
* 🧪 Prevention strategy

---

## 🎙 Voice Input (Optional)

To enable speech input:

```bash
pip install SpeechRecognition pyaudio
```

Click **🎙 VOICE** in the interface.

---

## 📊 Session Memory

* Stores last **30 exchanges**
* Displays:

  * Query count
  * Message count
  * Memory usage %
  * Last response time

---

## 🎨 UI System

CyberBot includes:

* Custom CSS engine
* Cyberpunk neon gradients
* Animated skyline SVG
* Glowing code windows
* Token streaming animation
* Neural thought panels

Color Palette:

* Electric Cyan — `#00E8FF`
* Hot Magenta — `#FF0080`
* Nebula Violet — `#7B00D4`
* Circuit Green — `#39FF14`
* Solar Red — `#FF3D00`
* Deep Space — `#050912`

---

## ⚙ Configuration

Inside the script:

```python
APP_NAME    = "CyberBot"
APP_VER     = "v4.0"
MODEL       = "hf.co/MaziyarPanahi/codegemma-2b-GGUF:Q4_k_M"
MAX_HISTORY = 30
```

You can modify:

* Model
* Temperature
* Token limits
* Memory depth

---

## 🚀 Performance Tips

* Use Q4_k_M quantization for lower VRAM
* Reduce `num_predict` if memory constrained
* Adjust temperature for more deterministic outputs
* Disable thought rendering for faster UI

---

## 🧩 Troubleshooting

### Ollama Offline

Make sure:

```bash
ollama serve
```

is running before launching Streamlit.

---

### Model Not Found

```bash
ollama pull hf.co/MaziyarPanahi/codegemma-2b-GGUF:Q4_k_M
```

---

### Audio Errors

Install dependencies properly:

```bash
pip install SpeechRecognition pyaudio
```

---

## 📁 Project Structure

```
cyberbot/
│
├── app.py
├── README.md
└── requirements.txt
```

---

## 🛡 License

MIT License — free to use, modify, and distribute.

---

## 🌌 Inspiration

Inspired by:

* Cyberpunk neon city aesthetics
* Neural interfaces
* Hacker terminal UIs
* Local-first AI systems

---

## 🤝 Contributing

Pull requests welcome.

Suggested improvements:

* Syntax highlighting engine
* Model selector dropdown
* Chat export feature
* Docker deployment
* Multi-model support
* GPU performance monitor

---

## 🔮 Future Roadmap

* Multi-agent reasoning
* File upload + project analysis
* Persistent memory
* VS Code extension
* Remote API mode
* Dark/Light theme switcher
* Model benchmarking panel

---

# ⚡ CyberBot v4.0

**Jack into the neural grid. Build the future.**

---

# SLM-CYBERBOT
