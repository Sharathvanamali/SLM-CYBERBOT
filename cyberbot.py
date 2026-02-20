"""
╔══════════════════════════════════════════════════════════════════════╗
║  ░█▀▀░█░█░█▀▄░█▀▀░█▀▄░█▀▄░█▀█░▀█▀                                  ║
║  Model  : hf.co/MaziyarPanahi/codegemma-2b-GGUF:Q4_k_M             ║
║  Stack  : Ollama · Streamlit                                         ║
║  Theme  : Neo-Noir Cyberpunk City (kvacm inspired)                  ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import re, time, datetime, hashlib
import streamlit as st

try:
    import ollama as _ollama
    OLLAMA_PKG = True
except ImportError:
    OLLAMA_PKG = False

try:
    import speech_recognition as _sr
    AUDIO_PKG = True
except ImportError:
    AUDIO_PKG = False

# ═══════════════════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════════════════
APP_NAME    = "CyberBot"
APP_VER     = "v4.0"
MODEL       = "hf.co/MaziyarPanahi/codegemma-2b-GGUF:Q4_k_M"
MAX_HISTORY = 30

# ═══════════════════════════════════════════════════════════════════════
#  SYSTEM PROMPTS
# ═══════════════════════════════════════════════════════════════════════
BASE_SYSTEM = """You are CyberBot, an elite AI coding assistant and problem solver.

MANDATORY FORMATTING RULES:
1. Always wrap code in triple backtick fences with the language name:
   ```python
   # code here
   ```
2. Never truncate or abbreviate code. Write complete, runnable implementations.
3. Add comments to explain non-trivial logic inline.
4. After every code block, write a brief "How it works" explanation.
5. For algorithms always state: Time Complexity: O(?) and Space Complexity: O(?)

RESPONSE STRUCTURE:
- One-line direct answer first
- Then detailed explanation or full code
- End with a useful tip when relevant

ACCURACY: Think step by step before answering. If unsure, say so.
TONE: Professional, clear, precise. No unnecessary filler.
"""

DEEP_SYSTEM = BASE_SYSTEM + """
DEEP THOUGHT MODE ACTIVE. Structure EVERY response with:
**🔍 Problem Breakdown:** Understand what is being asked
**💡 Approach:** Strategy chosen and why
**⚙️ Implementation:** Full code/solution
**✅ Test Cases:** At least 2 to 3 examples with expected output
**🚀 Optimisations:** Improvements and alternatives
"""

CODE_SYSTEM = BASE_SYSTEM + """
CODE MASTER MODE ACTIVE. For every coding response:
- Write production-quality complete code only
- Include type hints, docstrings, and error handling
- Provide example usage in a separate code block labelled "Example"
- State time and space complexity clearly
- List edge cases your solution handles
"""

DEBUG_SYSTEM = BASE_SYSTEM + """
DEBUG MODE ACTIVE. For every debugging request:
**🐛 Root Cause:** What is causing the bug and where
**🔬 Analysis:** Why it happens with line-by-line breakdown if needed
**🔧 Fixed Code:** The COMPLETE corrected code in a code block
**🧪 Prevention:** How to avoid this class of bug in future
Always provide the full corrected file, not just the changed section.
"""

MODE_PROMPTS = {
    "Normal":       BASE_SYSTEM,
    "Deep Thought": DEEP_SYSTEM,
    "Code Master":  CODE_SYSTEM,
    "Debug":        DEBUG_SYSTEM,
}

# ═══════════════════════════════════════════════════════════════════════
#  CSS  — Full Neo-Noir Cyberpunk City Rebuild
#  Colour palette extracted from kvacm cyberpunk city artwork:
#  #050912 Deep Space | #00E8FF Electric Cyan | #FF0080 Hot Magenta
#  #7B00D4 Nebula Violet | #FF3D00 Solar Red | #39FF14 Circuit Green
#  #FFD700 Star Gold   | #0A1628 Dark Navy   | #E8F6FF Ice White
# ═══════════════════════════════════════════════════════════════════════
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Share+Tech+Mono&family=Rajdhani:wght@300;400;500;600;700&display=swap');

:root {
  --bg:     #050912;
  --navy:   #0A1628;
  --panel:  #0D1F3C;
  --cyan:   #00E8FF;
  --cyan2:  #00B8CC;
  --mag:    #FF0080;
  --pink:   #FF3D9A;
  --vio:    #7B00D4;
  --purp:   #B040FF;
  --red:    #FF3D00;
  --grn:    #39FF14;
  --gold:   #FFD700;
  --ice:    #E8F6FF;
  --dim:    rgba(232,246,255,0.45);
  --dimmer: rgba(232,246,255,0.2);
}

*, *::before, *::after { box-sizing: border-box; }

html, body {
  background: var(--bg) !important;
  font-family: 'Rajdhani', sans-serif !important;
  color: var(--ice) !important;
}

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: linear-gradient(180deg, var(--cyan), var(--vio)); border-radius: 4px; }

/* ── APP BACKGROUND: nebula + stars ─────────────────────────────── */
[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(ellipse 55% 30% at 65% 6%,  rgba(255,0,128,0.22) 0%, transparent 70%),
    radial-gradient(ellipse 40% 25% at 55% 4%,  rgba(123,0,212,0.30) 0%, transparent 65%),
    radial-gradient(ellipse 28% 15% at 80% 3%,  rgba(255,61,0,0.16)  0%, transparent 60%),
    radial-gradient(ellipse 55% 28% at 18% 92%, rgba(0,232,255,0.09)  0%, transparent 65%),
    radial-gradient(ellipse 45% 22% at 82% 88%, rgba(255,0,128,0.07)  0%, transparent 60%),
    linear-gradient(180deg, #050912 0%, #070D1C 45%, #050912 100%) !important;
  min-height: 100vh;
}

/* Scanlines */
[data-testid="stAppViewContainer"]::before {
  content: '';
  position: fixed; inset: 0;
  background: repeating-linear-gradient(0deg, transparent 0px, transparent 3px, rgba(0,232,255,0.012) 3px, rgba(0,232,255,0.012) 4px);
  pointer-events: none; z-index: 9999;
}

/* Star field */
[data-testid="stAppViewContainer"]::after {
  content: '';
  position: fixed; inset: 0; pointer-events: none; z-index: 9998;
  background-image:
    radial-gradient(1px 1px at  9%  7%, rgba(255,255,255,0.90) 0%, transparent 100%),
    radial-gradient(1px 1px at 22%  3%, rgba(255,255,255,0.70) 0%, transparent 100%),
    radial-gradient(1px 1px at 35% 11%, rgba(255,255,255,0.60) 0%, transparent 100%),
    radial-gradient(1px 1px at 47%  5%, rgba(255,255,255,0.80) 0%, transparent 100%),
    radial-gradient(1px 1px at 59%  2%, rgba(255,255,255,0.50) 0%, transparent 100%),
    radial-gradient(1px 1px at 72%  9%, rgba(255,255,255,0.75) 0%, transparent 100%),
    radial-gradient(1px 1px at 83%  4%, rgba(255,255,255,0.90) 0%, transparent 100%),
    radial-gradient(1px 1px at 94% 13%, rgba(255,255,255,0.60) 0%, transparent 100%),
    radial-gradient(1px 1px at  5% 17%, rgba(255,255,255,0.45) 0%, transparent 100%),
    radial-gradient(1px 1px at 16% 21%, rgba(255,255,255,0.80) 0%, transparent 100%),
    radial-gradient(1px 1px at 29% 15%, rgba(255,255,255,0.55) 0%, transparent 100%),
    radial-gradient(1px 1px at 42% 19%, rgba(255,255,255,0.70) 0%, transparent 100%),
    radial-gradient(1px 1px at 53% 14%, rgba(255,255,255,0.65) 0%, transparent 100%),
    radial-gradient(1px 1px at 66% 18%, rgba(255,255,255,0.85) 0%, transparent 100%),
    radial-gradient(1px 1px at 78% 10%, rgba(255,255,255,0.50) 0%, transparent 100%),
    radial-gradient(1px 1px at 89% 16%, rgba(255,255,255,0.90) 0%, transparent 100%),
    radial-gradient(2px 2px at 31%  6%, rgba(0,232,255,0.85)   0%, transparent 100%),
    radial-gradient(2px 2px at 62%  9%, rgba(255,0,128,0.75)   0%, transparent 100%),
    radial-gradient(2px 2px at 86%  5%, rgba(255,215,0,0.80)   0%, transparent 100%),
    radial-gradient(1px 1px at 74% 22%, rgba(255,255,255,0.40) 0%, transparent 100%),
    radial-gradient(1px 1px at 12%  8%, rgba(255,255,255,0.60) 0%, transparent 100%);
  animation: twinkle 7s ease-in-out infinite alternate;
}
@keyframes twinkle { from{opacity:0.6;} to{opacity:1.0;} }

/* ── LAYOUT ──────────────────────────────────────────────────────── */
[data-testid="stMain"] { padding: 0 !important; }
.block-container { padding: 0.75rem 1.25rem 1.5rem !important; max-width: 1300px !important; }
#MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }

/* ── SIDEBAR ─────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #06091A 0%, #080D1C 60%, #050912 100%) !important;
  border-right: 1px solid rgba(0,232,255,0.13) !important;
  box-shadow: 6px 0 40px rgba(0,232,255,0.04) !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label { color: var(--ice) !important; }

.sb { background: rgba(0,232,255,0.03); border: 1px solid rgba(0,232,255,0.11); border-left: 2px solid var(--cyan); border-radius: 6px; padding: 11px 13px; margin-bottom: 11px; }
.sbh { font-family:'Orbitron',sans-serif; font-size:0.54rem; letter-spacing:3px; color:var(--cyan); text-transform:uppercase; display:block; margin-bottom:9px; }

/* ── STATUS DOT ──────────────────────────────────────────────────── */
.dot { display:inline-block; width:7px; height:7px; border-radius:50%; margin-right:5px; vertical-align:middle; }
.don  { background:var(--grn);  box-shadow:0 0 8px var(--grn);  animation:pdot 2.5s ease-in-out infinite; }
.doff { background:var(--red);  box-shadow:0 0 6px var(--red);  }
@keyframes pdot { 0%,100%{box-shadow:0 0 5px var(--grn);} 50%{box-shadow:0 0 16px var(--grn),0 0 28px rgba(57,255,20,0.2);} }

/* ── METRICS ─────────────────────────────────────────────────────── */
.mrow  { display:flex; gap:6px; margin:7px 0; }
.mcard { flex:1; background:rgba(0,232,255,0.04); border:1px solid rgba(0,232,255,0.11); border-radius:5px; padding:7px 4px; text-align:center; }
.mval  { font-family:'Orbitron',sans-serif; font-size:1.05rem; font-weight:700; color:var(--gold); line-height:1; }
.mlbl  { font-size:0.50rem; letter-spacing:1.5px; color:var(--dimmer); text-transform:uppercase; margin-top:3px; }
.memb  { height:3px; background:rgba(0,232,255,0.09); border-radius:2px; overflow:hidden; margin:5px 0; }
.memf  { height:100%; border-radius:2px; background:linear-gradient(90deg,var(--cyan),var(--purp),var(--mag)); transition:width 0.5s; }

/* ── BADGES ──────────────────────────────────────────────────────── */
.badge { display:inline-block; padding:3px 9px; border-radius:3px; font-family:'Share Tech Mono',monospace; font-size:0.54rem; letter-spacing:2px; text-transform:uppercase; margin-top:5px; }
.bn { border:1px solid rgba(0,232,255,0.38);  color:var(--cyan);  background:rgba(0,232,255,0.07);  }
.bd { border:1px solid rgba(176,64,255,0.45); color:var(--purp);  background:rgba(176,64,255,0.07); }
.bc { border:1px solid rgba(57,255,20,0.38);  color:var(--grn);   background:rgba(57,255,20,0.06);  }
.bdb{ border:1px solid rgba(255,215,0,0.38);  color:var(--gold);  background:rgba(255,215,0,0.06);  }

/* ── BUTTONS ─────────────────────────────────────────────────────── */
.stButton > button {
  font-family:'Orbitron',sans-serif !important; font-size:0.58rem !important; font-weight:700 !important;
  letter-spacing:2px !important; text-transform:uppercase !important;
  background:transparent !important; border:1px solid rgba(0,232,255,0.38) !important;
  color:var(--cyan) !important; border-radius:5px !important; padding:9px 12px !important;
  width:100% !important; transition:all 0.2s ease !important;
  position:relative !important; overflow:hidden !important;
}
.stButton > button::before {
  content:''; position:absolute; inset:0;
  background:linear-gradient(90deg,transparent,rgba(0,232,255,0.09),transparent);
  transform:translateX(-100%); transition:transform 0.35s;
}
.stButton > button:hover::before { transform:translateX(100%); }
.stButton > button:hover {
  background:rgba(0,232,255,0.06) !important; border-color:var(--cyan) !important;
  box-shadow:0 0 18px rgba(0,232,255,0.18),inset 0 0 18px rgba(0,232,255,0.03) !important;
  transform:translateY(-1px) !important;
}
.stButton > button:active { transform:translateY(0) !important; }

.tx-btn .stButton > button {
  background:rgba(255,0,128,0.07) !important; border-color:rgba(255,0,128,0.45) !important;
  color:var(--mag) !important; font-size:0.62rem !important; padding:11px 16px !important;
}
.tx-btn .stButton > button:hover {
  background:rgba(255,0,128,0.13) !important;
  box-shadow:0 0 24px rgba(255,0,128,0.25),inset 0 0 18px rgba(255,0,128,0.04) !important;
}

.cl-btn .stButton > button {
  border-color:rgba(255,61,0,0.38) !important; color:var(--red) !important;
}
.cl-btn .stButton > button:hover { background:rgba(255,61,0,0.07) !important; box-shadow:0 0 16px rgba(255,61,0,0.18) !important; }

/* ── TEXTAREA ────────────────────────────────────────────────────── */
.stTextArea textarea {
  background:rgba(10,22,40,0.90) !important; border:1px solid rgba(0,232,255,0.18) !important;
  border-radius:6px !important; color:var(--ice) !important;
  font-family:'Rajdhani',sans-serif !important; font-size:0.98rem !important;
  line-height:1.55 !important; caret-color:var(--cyan) !important; resize:none !important;
  transition:border-color 0.25s,box-shadow 0.25s !important;
}
.stTextArea textarea:focus {
  border-color:rgba(0,232,255,0.45) !important;
  box-shadow:0 0 0 1px rgba(0,232,255,0.10),0 0 22px rgba(0,232,255,0.09) !important;
  outline:none !important;
}
.stTextArea textarea::placeholder { color:rgba(232,246,255,0.18) !important; }
.stTextArea label { display:none !important; }

/* ── HEADER ─────────────────────────────────────────────────────── */
.cb-hdr {
  position:relative; overflow:hidden;
  padding:20px 26px 18px; margin-bottom:14px;
  background:linear-gradient(135deg,rgba(5,9,18,0.97) 0%,rgba(10,22,40,0.97) 50%,rgba(5,9,18,0.97) 100%);
  border:1px solid rgba(0,232,255,0.18); border-bottom:2px solid rgba(0,232,255,0.32); border-radius:8px;
  box-shadow:0 0 55px rgba(0,232,255,0.06),0 0 110px rgba(255,0,128,0.03),inset 0 1px 0 rgba(0,232,255,0.09);
}
.cb-hdr::before {
  content:''; position:absolute; top:0; right:0; width:55%; height:100%;
  background:radial-gradient(ellipse 80% 100% at 80% 50%,rgba(255,0,128,0.09) 0%,transparent 70%),
             radial-gradient(ellipse 60% 80% at 50% 0%,  rgba(123,0,212,0.11) 0%,transparent 60%);
  pointer-events:none;
}
.cb-hdr::after {
  content:''; position:absolute; bottom:0; left:0; height:2px; width:0;
  background:linear-gradient(90deg,var(--cyan),var(--mag),var(--vio));
  animation:hdrline 2.5s ease-out forwards;
}
@keyframes hdrline { to{width:100%;} }

.cb-name {
  font-family:'Orbitron',sans-serif; font-size:clamp(1.8rem,4vw,3rem);
  font-weight:900; letter-spacing:12px;
  background:linear-gradient(90deg,var(--cyan) 0%,#80F4FF 22%,var(--ice) 48%,var(--mag) 72%,var(--purp) 100%);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
  position:relative; z-index:1; line-height:1.1;
  animation:flicker 9s ease-in-out infinite;
}
@keyframes flicker { 0%,87%,89%,91%,100%{opacity:1;} 88%,90%{opacity:0.65;} }

.cb-sub {
  font-family:'Share Tech Mono',monospace; font-size:0.66rem; letter-spacing:4px;
  color:rgba(0,232,255,0.58); margin-top:5px; position:relative; z-index:1;
}
.cb-pills {
  position:absolute; top:16px; right:18px; display:flex; gap:7px; align-items:center; z-index:1;
}
.cpill {
  font-family:'Share Tech Mono',monospace; font-size:0.56rem; letter-spacing:2px;
  padding:3px 9px; border-radius:20px; border:1px solid rgba(0,232,255,0.28);
  color:rgba(0,232,255,0.65); background:rgba(0,232,255,0.05);
}
.cpill.on  { border-color:rgba(57,255,20,0.45); color:var(--grn); background:rgba(57,255,20,0.05); }
.cpill.off { border-color:rgba(255,61,0,0.45);  color:var(--red); background:rgba(255,61,0,0.05); }

/* ── CHAT MESSAGES ───────────────────────────────────────────────── */
.mwrap { animation:mslide 0.28s cubic-bezier(0.2,1,0.4,1) both; margin-bottom:13px; }
@keyframes mslide { from{opacity:0;transform:translateY(11px);} to{opacity:1;transform:none;} }

.mu {
  margin-left:8%;
  background:linear-gradient(135deg,rgba(255,0,128,0.09) 0%,rgba(77,0,160,0.06) 100%);
  border:1px solid rgba(255,0,128,0.26); border-right:3px solid var(--mag);
  border-radius:10px 3px 10px 10px; padding:12px 15px 9px;
  box-shadow:0 4px 28px rgba(255,0,128,0.06),inset 0 1px 0 rgba(255,0,128,0.09);
}
.lu { font-family:'Share Tech Mono',monospace; font-size:0.54rem; letter-spacing:3px; color:var(--mag); display:block; margin-bottom:7px; }

.mai {
  margin-right:8%;
  background:linear-gradient(135deg,rgba(0,232,255,0.055) 0%,rgba(123,0,212,0.045) 100%);
  border:1px solid rgba(0,232,255,0.17); border-left:3px solid var(--cyan);
  border-radius:3px 10px 10px 10px; padding:12px 15px 9px;
  box-shadow:0 4px 28px rgba(0,232,255,0.055),inset 0 1px 0 rgba(0,232,255,0.08);
}
.lai { font-family:'Share Tech Mono',monospace; font-size:0.54rem; letter-spacing:3px; color:var(--cyan); display:block; margin-bottom:7px; }

.mbody { font-size:0.94rem; line-height:1.72; color:var(--ice); word-break:break-word; }
.mbody strong { color:var(--gold); }
.mbody em     { color:var(--cyan); font-style:italic; }

.mts { font-family:'Share Tech Mono',monospace; font-size:0.50rem; color:rgba(232,246,255,0.18); text-align:right; margin-top:6px; }

.dinfo {
  background:rgba(255,215,0,0.04); border:1px dashed rgba(255,215,0,0.22); border-radius:4px;
  margin-top:7px; padding:7px 11px;
  font-family:'Share Tech Mono',monospace; font-size:0.60rem; color:rgba(255,215,0,0.55); line-height:1.6;
}

/* ── THOUGHT BOX ─────────────────────────────────────────────────── */
.thgt {
  background:rgba(176,64,255,0.055); border:1px dashed rgba(176,64,255,0.32); border-radius:5px;
  padding:9px 13px; margin:9px 0;
  font-family:'Share Tech Mono',monospace; font-size:0.70rem; color:rgba(176,64,255,0.82); line-height:1.7;
}
.thgt-h { font-family:'Orbitron',monospace; font-size:0.50rem; letter-spacing:3px; color:var(--purp); display:block; margin-bottom:6px; }

/* ── CODE BLOCKS ─────────────────────────────────────────────────── */
.cwin { margin:11px 0; border-radius:2px 8px 8px 8px; overflow:hidden; border:1px solid rgba(57,255,20,0.16); box-shadow:0 8px 36px rgba(0,0,0,0.48),0 0 22px rgba(57,255,20,0.03); }
.cbar { display:flex; align-items:center; justify-content:space-between; background:rgba(57,255,20,0.055); border-bottom:1px solid rgba(57,255,20,0.13); padding:5px 11px; gap:9px; }
.cdots { display:flex; gap:4px; }
.cdot  { width:9px; height:9px; border-radius:50%; }
.cdot:nth-child(1){background:#FF5F57;} .cdot:nth-child(2){background:#FEBC2E;} .cdot:nth-child(3){background:#28C840;}
.clang { font-family:'Share Tech Mono',monospace; font-size:0.58rem; letter-spacing:2px; color:var(--grn); text-transform:uppercase; flex:1; text-align:center; }
.ctag  { font-family:'Share Tech Mono',monospace; font-size:0.51rem; color:rgba(57,255,20,0.38); letter-spacing:1px; }
.cbody { background:#04080F; padding:13px 15px; overflow-x:auto; font-family:'Share Tech Mono',monospace; font-size:0.79rem; line-height:1.8; color:#A8FFA8; white-space:pre; tab-size:4; }
.cbody::-webkit-scrollbar { height:3px; }
.cbody::-webkit-scrollbar-thumb { background:linear-gradient(90deg,var(--grn),var(--cyan)); border-radius:2px; }

/* Inline code */
.icod { background:rgba(57,255,20,0.08); border:1px solid rgba(57,255,20,0.20); color:var(--grn); font-family:'Share Tech Mono',monospace; font-size:0.82em; padding:1px 5px; border-radius:3px; }

/* Section headers in AI response */
.shdr { font-family:'Orbitron',sans-serif; font-size:0.72rem; font-weight:700; letter-spacing:1px; margin:13px 0 5px; padding-bottom:4px; border-bottom:1px solid rgba(0,232,255,0.13); color:var(--gold); display:block; }
.blt  { padding-left:9px; margin:2px 0; }

/* ── STREAMING ───────────────────────────────────────────────────── */
.sbox { margin-right:8%; background:linear-gradient(135deg,rgba(0,232,255,0.05) 0%,rgba(123,0,212,0.04) 100%); border:1px solid rgba(0,232,255,0.15); border-left:3px solid var(--cyan); border-radius:3px 10px 10px 10px; padding:12px 15px; }
.slbl { font-family:'Share Tech Mono',monospace; font-size:0.54rem; letter-spacing:3px; color:var(--cyan); display:block; margin-bottom:7px; }
.stxt { font-size:0.94rem; line-height:1.72; color:var(--ice); word-break:break-word; }
.cur  { display:inline-block; width:2px; height:1em; background:var(--cyan); box-shadow:0 0 7px var(--cyan); vertical-align:text-bottom; margin-left:2px; animation:cblink 0.75s step-end infinite; }
@keyframes cblink { 0%,100%{opacity:1;} 50%{opacity:0;} }

/* ── EMPTY STATE ─────────────────────────────────────────────────── */
.emp { text-align:center; padding:48px 20px 28px; }
.emp-ic { font-size:3rem; margin-bottom:11px; filter:drop-shadow(0 0 18px rgba(0,232,255,0.45)); }
.emp-t  { font-family:'Orbitron',sans-serif; font-size:0.95rem; letter-spacing:9px; color:rgba(0,232,255,0.20); margin-bottom:5px; }
.emp-s  { font-family:'Share Tech Mono',monospace; font-size:0.60rem; color:rgba(232,246,255,0.14); letter-spacing:2px; }
.chips  { display:flex; flex-wrap:wrap; gap:7px; justify-content:center; margin-top:18px; }
.chip   { background:rgba(10,22,40,0.80); border:1px solid rgba(0,232,255,0.16); border-radius:18px; padding:5px 12px; font-family:'Share Tech Mono',monospace; font-size:0.58rem; color:rgba(0,232,255,0.50); }

/* ── INPUT ZONE ──────────────────────────────────────────────────── */
.izone { background:rgba(10,22,40,0.55); border:1px solid rgba(0,232,255,0.11); border-top:2px solid rgba(0,232,255,0.18); border-radius:0 0 8px 8px; padding:13px 15px 11px; margin-top:3px; }
.itopbar { display:flex; align-items:center; gap:9px; margin-bottom:9px; }
.ilbl    { font-family:'Share Tech Mono',monospace; font-size:0.56rem; letter-spacing:2px; color:var(--dimmer); }

/* ── SKYLINE STRIP ───────────────────────────────────────────────── */
.sky { width:100%; height:72px; position:relative; overflow:hidden; margin-top:8px; }
.sky svg { width:100%; height:100%; }

/* ── DIVIDER ─────────────────────────────────────────────────────── */
.ndiv { height:1px; margin:11px 0; border:none; background:linear-gradient(90deg,transparent 0%,rgba(0,232,255,0.22) 30%,rgba(255,0,128,0.22) 70%,transparent 100%); }

/* ── FOOTER ──────────────────────────────────────────────────────── */
.fbar { font-family:'Share Tech Mono',monospace; font-size:0.53rem; letter-spacing:2px; color:rgba(232,246,255,0.16); text-align:center; margin-top:5px; }
.fglow { height:2px; margin-top:5px; background:linear-gradient(90deg,transparent,rgba(0,232,255,0.30),rgba(255,0,128,0.30),rgba(123,0,212,0.30),transparent); border-radius:2px; filter:blur(0.5px); }

/* ── MISC ────────────────────────────────────────────────────────── */
.stRadio label, .stToggle label { font-family:'Rajdhani',sans-serif !important; font-size:0.88rem !important; }
.stRadio div[role="radiogroup"] { gap:4px !important; }
[data-testid="column"] { padding:0 3px !important; }
.stAlert { background:rgba(10,22,40,0.9) !important; border-radius:6px !important; }
.stSelectbox div[data-baseweb="select"] > div { background:rgba(10,22,40,0.9) !important; border-color:rgba(0,232,255,0.20) !important; color:var(--ice) !important; border-radius:5px !important; }
</style>
"""

# ═══════════════════════════════════════════════════════════════════════
#  LANGUAGE MAP
# ═══════════════════════════════════════════════════════════════════════
LANG_MAP = {
    "python":"PYTHON","py":"PYTHON","javascript":"JAVASCRIPT","js":"JAVASCRIPT",
    "typescript":"TYPESCRIPT","ts":"TYPESCRIPT","java":"JAVA","c":"C","cpp":"C++",
    "c++":"C++","csharp":"C#","cs":"C#","go":"GOLANG","rust":"RUST","swift":"SWIFT",
    "kotlin":"KOTLIN","ruby":"RUBY","rb":"RUBY","php":"PHP","r":"R","sql":"SQL",
    "html":"HTML","css":"CSS","bash":"BASH","sh":"BASH","shell":"SHELL",
    "json":"JSON","yaml":"YAML","yml":"YAML","xml":"XML","markdown":"MARKDOWN",
    "md":"MARKDOWN","text":"TEXT","txt":"TEXT","":"CODE",
}

CODE_RE   = re.compile(r'```(\w*)\n?(.*?)```', re.DOTALL)
INLINE_RE = re.compile(r'`([^`\n]+)`')
BOLD_RE   = re.compile(r'\*\*(.+?)\*\*')
ITALIC_RE = re.compile(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)')

SECTION_ICONS = ['🔍','💡','⚙️','✅','🚀','📌','⚠️','🔧','📊','🐛','🔬','🧪']

def _esc(t: str) -> str:
    return t.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def code_block_html(lang_raw: str, code: str) -> str:
    lbl  = LANG_MAP.get(lang_raw.lower().strip(), lang_raw.upper() or "CODE")
    body = _esc(code.rstrip())
    return (
        f'<div class="cwin">'
        f'<div class="cbar">'
        f'<div class="cdots"><div class="cdot"></div><div class="cdot"></div><div class="cdot"></div></div>'
        f'<span class="clang">// {lbl}</span>'
        f'<span class="ctag">CYBERBOT GENERATED</span>'
        f'</div>'
        f'<div class="cbody">{body}</div>'
        f'</div>'
    )

def format_ai_text(text: str) -> str:
    # 1. Fenced code blocks
    text = CODE_RE.sub(lambda m: code_block_html(m.group(1), m.group(2)), text)
    # 2. Bold / italic
    text = BOLD_RE.sub(r'<strong>\1</strong>', text)
    text = ITALIC_RE.sub(r'<em>\1</em>', text)
    # 3. Inline code
    text = INLINE_RE.sub(lambda m: f'<span class="icod">{_esc(m.group(1))}</span>', text)
    # 4. Line processing
    out = []
    for line in text.split('\n'):
        s = line.strip()
        if any(s.startswith(ic) for ic in SECTION_ICONS):
            out.append(f'<span class="shdr">{s}</span>')
        elif re.match(r'^[•\-\*]\s', s) and not s.startswith('**'):
            out.append(f'<div class="blt">▸ {s[2:]}</div>')
        elif re.match(r'^\d+\.\s', s):
            out.append(f'<div class="blt">{s}</div>')
        else:
            out.append(line)
    return '<br>'.join(out)

def split_thoughts(text: str):
    markers = [
        '🔍 Problem Breakdown','🔍 ANALYSIS','💡 Approach','💡 APPROACH',
        '⚙️ Implementation','⚙️ SOLUTION','✅ Test Cases','✅ VERIFICATION',
        '🚀 Optimisations','🚀 OPTIMISATION','🐛 Root Cause','🔬 Analysis',
        '🔧 Fix','🔧 Fixed Code','🧪 Prevention','[ANALYSIS]','[APPROACH]',
    ]
    thought, main, in_t = [], [], False
    for line in text.split('\n'):
        if any(line.strip().startswith(m) for m in markers):
            in_t = True
        (thought if in_t else main).append(line)
        if in_t and line.strip() == '' and len(thought) > 1:
            in_t = False
    if not thought:
        return text, None
    return (
        '\n'.join(main).strip(),
        '<div class="thgt"><span class="thgt-h">◈ NEURAL THOUGHT PROCESS</span>'
        + '\n'.join(thought).replace('\n','<br>') + '</div>'
    )

# ═══════════════════════════════════════════════════════════════════════
#  OLLAMA
# ═══════════════════════════════════════════════════════════════════════
def check_ollama() -> bool:
    if not OLLAMA_PKG:
        return False
    try:
        _ollama.list()
        return True
    except Exception:
        return False

def build_msgs(history: list, user_text: str, mode: str) -> list:
    msgs = [{"role": "system", "content": MODE_PROMPTS.get(mode, BASE_SYSTEM)}]
    for m in history[-MAX_HISTORY:]:
        msgs.append({"role": m["role"], "content": m["content"]})
    msgs.append({"role": "user", "content": user_text})
    return msgs

def stream_response(messages: list):
    stream = _ollama.chat(
        model=MODEL, messages=messages, stream=True,
        options={"temperature":0.65,"top_p":0.92,"top_k":40,
                 "repeat_penalty":1.1,"num_predict":4096,"stop":[]},
    )
    for chunk in stream:
        tok = chunk.get("message",{}).get("content","")
        if tok:
            yield tok

# ═══════════════════════════════════════════════════════════════════════
#  AUDIO
# ═══════════════════════════════════════════════════════════════════════
def capture_voice():
    if not AUDIO_PKG:
        return "[AUDIO_PKG_MISSING]"
    r = _sr.Recognizer(); r.energy_threshold=300; r.pause_threshold=0.9
    try:
        with _sr.Microphone() as src:
            r.adjust_for_ambient_noise(src, duration=0.4)
            audio = r.listen(src, timeout=10, phrase_time_limit=60)
        return r.recognize_google(audio)
    except _sr.WaitTimeoutError:   return None
    except _sr.UnknownValueError:  return None
    except Exception as e:         return f"[ERROR: {e}]"

# ═══════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ═══════════════════════════════════════════════════════════════════════
def init_state():
    defs = {
        "messages":      [],
        "session_id":    hashlib.md5(str(time.time()).encode()).hexdigest()[:8].upper(),
        "query_count":   0,
        "mode":          "Normal",
        "show_thoughts": True,
        "debug_mode":    False,
        "pending_audio": None,
        "last_elapsed":  0.0,
    }
    for k, v in defs.items():
        if k not in st.session_state:
            st.session_state[k] = v

def clear_chat():
    st.session_state.messages    = []
    st.session_state.query_count = 0
    st.session_state.last_elapsed= 0.0
    st.session_state.session_id  = hashlib.md5(str(time.time()).encode()).hexdigest()[:8].upper()

# ═══════════════════════════════════════════════════════════════════════
#  SKYLINE SVG
# ═══════════════════════════════════════════════════════════════════════
SKYLINE = """
<div class="sky">
<svg viewBox="0 0 1400 72" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="wg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#00E8FF" stop-opacity="0.45"/>
      <stop offset="100%" stop-color="#00E8FF" stop-opacity="0.0"/>
    </linearGradient>
    <filter id="ng"><feGaussianBlur stdDeviation="1.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>
  <path d="M0,72 L0,48 L18,48 L18,28 L26,28 L26,18 L34,18 L34,12 L42,12 L42,18 L50,18 L50,28 L58,28 L58,48
           L70,48 L70,38 L78,38 L78,22 L84,22 L84,15 L92,15 L92,22 L98,22 L98,38 L108,38 L108,48
           L120,48 L120,42 L128,42 L128,30 L135,30 L135,18 L140,18 L140,10 L146,10 L146,6  L152,6  L152,10 L158,10 L158,18 L163,18 L163,30 L170,30 L170,42 L178,42 L178,48
           L190,48 L190,52 L200,52 L200,38 L207,38 L207,28 L215,28 L215,38 L222,38 L222,52 L235,52
           L245,52 L245,45 L255,45 L255,25 L260,25 L260,16 L268,16 L268,8  L275,8  L275,4  L282,4  L282,8  L290,8  L290,16 L297,16 L297,25 L302,25 L302,45 L312,45 L312,52
           L325,52 L325,48 L335,48 L335,32 L342,32 L342,22 L350,22 L350,14 L356,14 L356,22 L364,22 L364,32 L370,32 L370,48 L382,48 L382,52
           L395,52 L395,45 L404,45 L404,34 L411,34 L411,26 L419,26 L419,34 L426,34 L426,45 L436,45 L436,52
           L448,52 L448,48 L458,48 L458,30 L463,30 L463,20 L470,20 L470,12 L478,12 L478,7  L485,7  L485,12 L493,12 L493,20 L500,20 L500,30 L505,30 L505,48 L515,48 L515,52
           L528,52 L528,46 L537,46 L537,35 L544,35 L544,28 L552,28 L552,35 L559,35 L559,46 L568,46 L568,52
           L580,52 L580,48 L590,48 L590,26 L595,26 L595,17 L602,17 L602,9  L610,9  L610,5  L617,5  L617,9  L625,9  L625,17 L632,17 L632,26 L637,26 L637,48 L647,48 L647,52
           L660,52 L660,47 L669,47 L669,36 L676,36 L676,29 L684,29 L684,36 L691,36 L691,47 L700,47 L700,52
           L712,52 L712,48 L722,48 L722,35 L728,35 L728,24 L735,24 L735,15 L742,15 L742,10 L750,10 L750,6  L757,6  L757,10 L765,10 L765,15 L772,15 L772,24 L778,24 L778,35 L784,35 L784,48 L795,48 L795,52
           L808,52 L808,46 L817,46 L817,35 L824,35 L824,28 L832,28 L832,35 L839,35 L839,46 L848,46 L848,52
           L860,52 L860,48 L870,48 L870,28 L875,28 L875,18 L882,18 L882,10 L890,10 L890,5  L897,5  L897,10 L905,10 L905,18 L912,18 L912,28 L917,28 L917,48 L927,48 L927,52
           L940,52 L940,46 L949,46 L949,36 L956,36 L956,29 L964,29 L964,36 L971,36 L971,46 L980,46 L980,52
           L992,52 L992,48 L1002,48 L1002,30 L1007,30 L1007,20 L1014,20 L1014,11 L1022,11 L1022,6  L1029,6  L1029,11 L1037,11 L1037,20 L1044,20 L1044,30 L1049,30 L1049,48 L1059,48 L1059,52
           L1072,52 L1072,46 L1081,46 L1081,35 L1088,35 L1088,28 L1096,28 L1096,35 L1103,35 L1103,46 L1112,46 L1112,52
           L1124,52 L1124,48 L1134,48 L1134,26 L1139,26 L1139,16 L1146,16 L1146,8  L1154,8  L1154,3  L1161,3  L1161,8  L1169,8  L1169,16 L1176,16 L1176,26 L1181,26 L1181,48 L1191,48 L1191,52
           L1204,52 L1204,46 L1213,46 L1213,36 L1220,36 L1220,29 L1228,29 L1228,36 L1235,36 L1235,46 L1244,46 L1244,52
           L1256,52 L1256,48 L1266,48 L1266,34 L1272,34 L1272,22 L1280,22 L1280,14 L1286,14 L1286,22 L1294,22 L1294,34 L1299,34 L1299,48 L1310,48 L1310,52
           L1322,52 L1322,46 L1331,46 L1331,38 L1340,38 L1340,46 L1349,46 L1349,52
           L1360,52 L1360,48 L1370,48 L1370,35 L1380,35 L1380,48 L1400,48 L1400,72 Z"
    fill="#060A18"/>
  <!-- Cyan neon edge highlights on tallest towers -->
  <path d="M140,10 L146,6 L152,10 M275,8 L282,4 L290,8 M478,7 L485,7 M750,6 L757,6 M890,5 L897,5 M1022,6 L1029,6 M1154,3 L1161,3"
    stroke="url(#wg)" stroke-width="1.2" fill="none" filter="url(#ng)" opacity="0.9"/>
  <!-- Cyan building windows -->
  <g fill="rgba(0,232,255,0.38)" filter="url(#ng)">
    <rect x="142" y="12" width="3" height="2"/> <rect x="148" y="12" width="3" height="2"/>
    <rect x="142" y="16" width="3" height="2"/> <rect x="148" y="16" width="3" height="2"/>
    <rect x="277" y="10" width="3" height="2"/> <rect x="283" y="10" width="3" height="2"/> <rect x="288" y="10" width="3" height="2"/>
    <rect x="277" y="14" width="3" height="2"/> <rect x="283" y="14" width="3" height="2"/> <rect x="288" y="14" width="3" height="2"/>
    <rect x="277" y="18" width="3" height="2"/> <rect x="283" y="18" width="3" height="2"/>
    <rect x="892" y="7"  width="3" height="2"/> <rect x="897" y="7"  width="3" height="2"/>
    <rect x="892" y="11" width="3" height="2"/> <rect x="897" y="11" width="3" height="2"/> <rect x="902" y="11" width="3" height="2"/>
    <rect x="892" y="15" width="3" height="2"/> <rect x="897" y="15" width="3" height="2"/> <rect x="902" y="15" width="3" height="2"/>
    <rect x="1024" y="8"  width="3" height="2"/> <rect x="1030" y="8"  width="3" height="2"/>
    <rect x="1024" y="12" width="3" height="2"/> <rect x="1030" y="12" width="3" height="2"/> <rect x="1036" y="12" width="3" height="2"/>
    <rect x="1156" y="5"  width="3" height="2"/> <rect x="1162" y="5"  width="3" height="2"/>
    <rect x="1156" y="9"  width="3" height="2"/> <rect x="1162" y="9"  width="3" height="2"/> <rect x="1168" y="9" width="3" height="2"/>
    <rect x="1156" y="13" width="3" height="2"/> <rect x="1162" y="13" width="3" height="2"/>
  </g>
  <!-- Magenta signal lights on towers -->
  <g fill="rgba(255,0,128,0.80)" filter="url(#ng)">
    <circle cx="146" cy="6"  r="1.8"/>
    <circle cx="282" cy="4"  r="2.0"/>
    <circle cx="485" cy="7"  r="1.6"/>
    <circle cx="897" cy="5"  r="2.0"/>
    <circle cx="1029" cy="6" r="1.8"/>
    <circle cx="1161" cy="3" r="2.2"/>
  </g>
  <!-- Water reflection glow -->
  <rect x="0" y="64" width="1400" height="8" fill="url(#wg)" opacity="0.35"/>
</svg>
</div>
"""

# ═══════════════════════════════════════════════════════════════════════
#  UI: HEADER
# ═══════════════════════════════════════════════════════════════════════
def render_header():
    online = check_ollama()
    pill_cls = "on" if online else "off"
    pill_txt = "● ONLINE" if online else "● OFFLINE"
    now = datetime.datetime.now().strftime("%Y·%m·%d %H:%M")
    st.markdown(
        f'<div class="cb-hdr">'
        f'<div class="cb-pills">'
        f'<span class="cpill">{APP_VER}</span>'
        f'<span class="cpill">{now}</span>'
        f'<span class="cpill {pill_cls}">{pill_txt}</span>'
        f'</div>'
        f'<div class="cb-name">CyberBot</div>'
        f'<div class="cb-sub">NEURAL CODE INTERFACE &nbsp;·&nbsp; CODEGEMMA-2B &nbsp;·&nbsp; MODE: {st.session_state.mode.upper()} &nbsp;·&nbsp; SID:{st.session_state.session_id}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ═══════════════════════════════════════════════════════════════════════
#  UI: SIDEBAR
# ═══════════════════════════════════════════════════════════════════════
def render_sidebar():
    with st.sidebar:
        # Status
        online = check_ollama()
        d_cls  = "don" if online else "doff"
        d_col  = "#39FF14" if online else "#FF3D00"
        d_txt  = "OLLAMA  ONLINE" if online else "OLLAMA  OFFLINE"
        st.markdown(
            f'<div class="sb"><span class="sbh">◈ System Status</span>'
            f'<p style="font-family:Share Tech Mono,monospace;font-size:0.73rem;">'
            f'<span class="dot {d_cls}"></span><span style="color:{d_col};">{d_txt}</span></p>'
            f'<p style="font-family:Share Tech Mono,monospace;font-size:0.61rem;color:rgba(0,232,255,0.52);margin-top:2px;">⬡ CODEGEMMA-2B-Q4_K_M</p>'
            + ('' if online else
               '<p style="font-family:Share Tech Mono,monospace;font-size:0.57rem;'
               'color:rgba(255,61,0,0.60);margin-top:3px;">Run: ollama serve</p>')
            + '</div>',
            unsafe_allow_html=True,
        )

        # Metrics
        cnt = len(st.session_state.messages)
        pct = min(100, int(cnt / MAX_HISTORY * 100))
        st.markdown(
            f'<div class="sb"><span class="sbh">◈ Session Metrics</span>'
            f'<div class="mrow">'
            f'<div class="mcard"><div class="mval">{st.session_state.query_count}</div><div class="mlbl">Queries</div></div>'
            f'<div class="mcard"><div class="mval">{cnt}</div><div class="mlbl">Msgs</div></div>'
            f'<div class="mcard"><div class="mval">{pct}%</div><div class="mlbl">Mem</div></div>'
            f'</div>'
            f'<div class="memb"><div class="memf" style="width:{pct}%;"></div></div>'
            + (f'<p style="font-family:Share Tech Mono,monospace;font-size:0.60rem;color:rgba(255,215,0,0.60);margin-top:5px;">⏱ Last: {st.session_state.last_elapsed}s</p>' if st.session_state.last_elapsed > 0 else '')
            + '</div>',
            unsafe_allow_html=True,
        )

        # Mode
        modes = ["Normal", "Deep Thought", "Code Master", "Debug"]
        st.markdown('<div class="sb"><span class="sbh">◈ Operation Mode</span>', unsafe_allow_html=True)
        mode = st.radio("Mode", modes, index=modes.index(st.session_state.mode), label_visibility="collapsed")
        st.session_state.mode = mode
        bcls = {"Normal":"bn","Deep Thought":"bd","Code Master":"bc","Debug":"bdb"}
        blbl = {"Normal":"STANDARD","Deep Thought":"DEEP THOUGHT","Code Master":"CODE MASTER","Debug":"DEBUG MODE"}
        st.markdown(f'<span class="badge {bcls[mode]}">{blbl[mode]}</span></div>', unsafe_allow_html=True)

        # Settings
        st.markdown('<div class="sb"><span class="sbh">◈ Display</span>', unsafe_allow_html=True)
        st.session_state.show_thoughts = st.toggle("Thought Process", value=st.session_state.show_thoughts)
        st.session_state.debug_mode    = st.toggle("Debug Info Panel",  value=st.session_state.debug_mode)
        st.markdown('</div>', unsafe_allow_html=True)

        # Actions
        st.markdown('<div class="sb"><span class="sbh">◈ Actions</span>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⟳ Reload", key="sb_rld"):
                st.rerun()
        with c2:
            st.markdown('<div class="cl-btn">', unsafe_allow_html=True)
            if st.button("✕ Clear", key="sb_clr"):
                clear_chat(); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Tips
        st.markdown(
            '<div style="padding:6px 2px;font-family:Share Tech Mono,monospace;'
            'font-size:0.54rem;color:rgba(232,246,255,0.22);line-height:2.0;">'
            '▸ Normal — general Q&amp;A<br>'
            '▸ Deep Thought — structured reasoning<br>'
            '▸ Code Master — full implementations<br>'
            '▸ Debug — root cause analysis &amp; fix<br>'
            '▸ Memory: last 30 exchanges kept</div>',
            unsafe_allow_html=True,
        )

# ═══════════════════════════════════════════════════════════════════════
#  UI: RENDER ONE MESSAGE
# ═══════════════════════════════════════════════════════════════════════
def render_message(role: str, content: str, ts: str = "", meta: dict = None):
    if role == "user":
        st.markdown(
            f'<div class="mwrap"><div class="mu"><span class="lu">⬡ YOU</span>'
            f'<div class="mbody">{_esc(content)}</div>'
            f'<div class="mts">{ts}</div></div></div>',
            unsafe_allow_html=True,
        )
    else:
        main_text, thought_html = split_thoughts(content)
        formatted = format_ai_text(main_text)

        t_sec = ""
        if thought_html and st.session_state.get("show_thoughts", True):
            t_sec = thought_html

        d_sec = ""
        if st.session_state.get("debug_mode", False) and meta:
            d_sec = (
                f'<div class="dinfo">'
                f'⏱ {meta.get("elapsed","?")}s elapsed &nbsp;|&nbsp; '
                f'✎ {meta.get("chars",0)} chars &nbsp;|&nbsp; '
                f'◈ {meta.get("mode","?")} mode &nbsp;|&nbsp; '
                f'⬡ codegemma-2b-q4_k_m'
                f'</div>'
            )

        st.markdown(
            f'<div class="mwrap"><div class="mai"><span class="lai">⚡ CYBERBOT</span>'
            f'{t_sec}'
            f'<div class="mbody">{formatted}</div>'
            f'{d_sec}'
            f'<div class="mts">{ts}</div></div></div>',
            unsafe_allow_html=True,
        )

# ═══════════════════════════════════════════════════════════════════════
#  UI: RENDER CHAT HISTORY
# ═══════════════════════════════════════════════════════════════════════
def render_chat():
    if not st.session_state.messages:
        st.markdown(
            '<div class="emp">'
            '<div class="emp-ic">🌆</div>'
            '<div class="emp-t">CYBERBOT</div>'
            '<div class="emp-s">JACK INTO THE NEURAL GRID — ASK ANYTHING</div>'
            '<div class="chips">'
            '<span class="chip">Binary search in Python</span>'
            '<span class="chip">Explain async/await</span>'
            '<span class="chip">Design a REST API</span>'
            '<span class="chip">Debug my code</span>'
            '<span class="chip">Quicksort explained</span>'
            '<span class="chip">Linked list implementation</span>'
            '</div></div>',
            unsafe_allow_html=True,
        )
        return
    for msg in st.session_state.messages:
        render_message(msg["role"], msg["content"], msg.get("ts",""), msg.get("meta"))

# ═══════════════════════════════════════════════════════════════════════
#  CORE: HANDLE SEND
# ═══════════════════════════════════════════════════════════════════════
def handle_send(user_text: str):
    user_text = user_text.strip()
    if not user_text:
        st.warning("⚠ Input is empty — type a question or paste code.")
        return

    if not check_ollama():
        st.error(
            "🔴 **CyberBot Offline** — Ollama is not running.\n\n"
            "**Start it:** `ollama serve`\n\n"
            "**Pull model (first time):**\n"
            "`ollama pull hf.co/MaziyarPanahi/codegemma-2b-GGUF:Q4_k_M`"
        )
        return

    ts = datetime.datetime.now().strftime("%H:%M:%S")
    st.session_state.messages.append({"role":"user","content":user_text,"ts":ts})
    st.session_state.query_count += 1
    render_message("user", user_text, ts)

    history = st.session_state.messages[:-1]
    msgs    = build_msgs(history, user_text, st.session_state.mode)

    ph         = st.empty()
    full_text  = ""
    char_acc   = 0
    start      = time.time()

    try:
        for tok in stream_response(msgs):
            full_text += tok
            char_acc  += len(tok)
            if char_acc % 60 < len(tok) or len(full_text) < 80:
                elapsed = round(time.time() - start, 1)
                ph.markdown(
                    f'<div class="sbox"><span class="slbl">⚡ CYBERBOT  —  THINKING... ({elapsed}s)</span>'
                    f'<div class="stxt">{_esc(full_text)}<span class="cur"></span></div></div>',
                    unsafe_allow_html=True,
                )
    except Exception as exc:
        full_text += f"\n\n**[ERROR]:** Could not reach Ollama model.\n\nDetails: {exc}"

    ph.empty()
    elapsed_f = round(time.time() - start, 2)
    final_ts  = f"{datetime.datetime.now().strftime('%H:%M:%S')}  [{elapsed_f}s]"
    meta = {"elapsed": elapsed_f, "chars": len(full_text), "mode": st.session_state.mode}

    st.session_state.messages.append({"role":"assistant","content":full_text,"ts":final_ts,"meta":meta})
    st.session_state.last_elapsed = elapsed_f

    if len(st.session_state.messages) > MAX_HISTORY * 2:
        st.session_state.messages = st.session_state.messages[-(MAX_HISTORY * 2):]

    st.rerun()

# ═══════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════
def main():
    st.set_page_config(
        page_title="CyberBot — Neural Interface",
        page_icon="🌆", layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(CSS, unsafe_allow_html=True)
    init_state()
    render_sidebar()
    render_header()
    render_chat()
    st.markdown(SKYLINE, unsafe_allow_html=True)
    st.markdown('<div class="ndiv"></div>', unsafe_allow_html=True)

    # Input toolbar label
    badge_cls = {"Normal":"bn","Deep Thought":"bd","Code Master":"bc","Debug":"bdb"}
    st.markdown(
        f'<div class="itopbar"><span class="ilbl">◈ INPUT TERMINAL</span>'
        f'<span class="badge {badge_cls[st.session_state.mode]}">{st.session_state.mode.upper()}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    audio_val  = st.session_state.pop("pending_audio", None) or ""
    user_input = st.text_area(
        "Input", value=audio_val, key="uibox",
        placeholder="// Ask anything, paste code to debug, describe a problem...\n// Supports: Python, JS, Java, C++, SQL, Rust, Go, Bash and more",
        height=120, label_visibility="collapsed",
    )

    # Button row — 4 columns: TRANSMIT | VOICE | CLEAR | (spacer)
    c_tx, c_vc, c_cl, _ = st.columns([2.4, 1.0, 1.0, 3.5])

    with c_tx:
        st.markdown('<div class="tx-btn">', unsafe_allow_html=True)
        send = st.button("⚡  TRANSMIT", key="btn_tx", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_vc:
        voice = st.button("🎙 VOICE", key="btn_vc", use_container_width=True)

    with c_cl:
        st.markdown('<div class="cl-btn">', unsafe_allow_html=True)
        clr = st.button("✕ CLEAR", key="btn_cl", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Events
    if clr:
        clear_chat(); st.rerun()

    if voice:
        if not AUDIO_PKG:
            st.error("Install audio deps: `pip install SpeechRecognition pyaudio`")
        else:
            with st.spinner("🎙 Listening... speak now"):
                result = capture_voice()
            if result and not result.startswith("["):
                st.success(f"✓ Heard: \"{result}\"")
                st.session_state.pending_audio = result
                st.rerun()
            elif result:
                st.error(f"Audio error: {result}")
            else:
                st.warning("No speech detected — please try again.")

    if send:
        handle_send(user_input)

    st.markdown(
        '<div class="fglow"></div>'
        '<div class="fbar">TRANSMIT to send &nbsp;·&nbsp; VOICE for speech input &nbsp;·&nbsp;'
        ' CLEAR to reset &nbsp;·&nbsp; DEBUG mode for code analysis &nbsp;·&nbsp; CYBERBOT v4.0</div>',
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    main()