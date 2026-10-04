import math
import streamlit as st

SAMPLES = {
    "grant": "Congratulations! You have won Rs. 50,000 in the BISP grant. Send your OTP and pay Rs. 500 processing fee within 2 hours at bit.ly/claim-now or your account will be blocked.",
    "bank": "Dear customer, your bank account will be blocked today. Verify immediately by sharing the OTP code sent to you at http://secure-bank-login.xyz",
    "safe": "Hi, are we still meeting at 5 pm today? I will bring the documents.",
}

SHIELD = ("<svg viewBox='0 0 64 72' width='64' height='72'>"
          "<path d='M32 3 L58 12 V34 C58 52 46 64 32 69 C18 64 6 52 6 34 V12 Z' fill='#0b1f4d' stroke='#f3c24b' stroke-width='3.5'/>"
          "<path d='M32 16 C38 27 45 31 43 42 C42 50 37 55 32 55 C26 55 21 50 22 42 C23 36 28 35 29 29 C30 25 31 21 32 16 Z' fill='#f06a2c'/>"
          "<path d='M32 30 C35 36 38 38 37 44 C36 48 34 50 32 50 C29 50 27 47 28 43 C29 39 31 38 32 30 Z' fill='#ffd54a'/></svg>")

def inject_css():
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');
    .stApp, .stMarkdown, p, label, button, textarea, input, h1, h2, h3 {font-family:'Poppins',sans-serif;}
    #MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] {display:none !important;}
    .stApp {background:
        radial-gradient(circle at 8% 10%, rgba(45,212,191,0.22), transparent 38%),
        radial-gradient(circle at 92% 18%, rgba(129,140,248,0.22), transparent 40%),
        radial-gradient(circle at 80% 92%, rgba(244,114,182,0.14), transparent 40%),
        linear-gradient(180deg,#f3f8fd,#eaf0fa);
        background-attachment: fixed;}
    .block-container {max-width: 880px; padding-top: 1.6rem;}

    .hero {position:relative; overflow:hidden; border-radius:22px; padding:30px 34px; margin-bottom:22px;
           background: radial-gradient(circle at 85% 0%, rgba(45,212,191,0.45), transparent 45%),
                       radial-gradient(circle at 0% 100%, rgba(129,140,248,0.45), transparent 50%),
                       linear-gradient(135deg,#070f2b,#14246b);
           border:1.5px solid rgba(243,194,75,0.7);
           box-shadow: 0 18px 40px rgba(10,25,80,0.35), inset 0 0 0 1px rgba(255,255,255,0.06);}
    .hero .row {display:flex; align-items:center; gap:18px;}
    .hero h1 {margin:0; font-size:3rem; font-weight:800; letter-spacing:-0.5px;
              background:linear-gradient(90deg,#ffe9a8,#f3b630); -webkit-background-clip:text;
              -webkit-text-fill-color:transparent;}
    .hero .tag {color:#cfe3ff; font-size:1.05rem; margin:8px 0 0 0; font-weight:500;}
    .hero .note {color:#9fb6e0; font-size:0.82rem; margin:10px 0 0 0; line-height:1.5;}
    .chips {display:flex; flex-wrap:wrap; gap:10px; margin-top:18px;}
    .chip {background:rgba(255,255,255,0.10); border:1px solid rgba(255,255,255,0.22); color:#fff;
           padding:6px 14px; border-radius:999px; font-size:0.82rem; font-weight:500; backdrop-filter:blur(4px);}

    .steps {display:flex; gap:14px; margin:6px 0 20px 0; flex-wrap:wrap;}
    .step {flex:1; min-width:200px; background:rgba(255,255,255,0.75); border:1px solid rgba(15,107,102,0.18);
           border-radius:16px; padding:14px 16px; box-shadow:0 6px 18px rgba(30,60,120,0.08);}
    .step b {color:#0b1f4d;} .step span {color:#4a5a73; font-size:0.85rem;}
    .step .ico {font-size:1.5rem;}

    .sec {display:flex; align-items:center; gap:12px; margin:26px 0 10px 0;}
    .sec .num {width:34px; height:34px; border-radius:50%; display:flex; align-items:center; justify-content:center;
               color:#fff; font-weight:700; background:linear-gradient(135deg,#14b8a6,#4f46e5);
               box-shadow:0 4px 10px rgba(79,70,229,0.35);}
    .sec .txt {font-size:1.25rem; font-weight:700; color:#0b1f4d;}

    .card {background:rgba(255,255,255,0.82); backdrop-filter:blur(6px); border-radius:16px;
           border:1px solid rgba(15,107,102,0.18); border-left:6px solid #14b8a6;
           padding:16px 22px; margin:12px 0; box-shadow:0 8px 22px rgba(30,60,120,0.10); color:#1d2b3a;}
    .card h4 {margin:0 0 8px 0; color:#0b1f4d; font-size:1.05rem; font-weight:700;}

    .flag {display:flex; align-items:center; gap:10px; padding:8px 0; border-bottom:1px solid #edf1f7;}
    .flag:last-child {border-bottom:none;}
    .pill {color:#fff; font-size:0.72rem; font-weight:700; padding:3px 10px; border-radius:999px; white-space:nowrap;}

    [data-testid="stFileUploader"] section {background:rgba(255,255,255,0.8); border-radius:14px;
           border:2px dashed #14b8a6;}
    .stTextArea textarea {background:rgba(255,255,255,0.9); border-radius:14px; border:2px solid #14b8a6; color:#13293d;}
    div[data-baseweb="select"] > div {background:#fff; border:2px solid #7c6cf0; border-radius:12px;}
    .stApp label p {color:#1d3b4a; font-weight:600;}

    [data-testid="stBaseButton-primary"] {background:linear-gradient(90deg,#f0a30a,#f0662a); color:#fff; font-weight:700;
           border:none; border-radius:14px; padding:0.8rem 2rem; font-size:1.05rem;
           box-shadow:0 10px 22px rgba(240,102,42,0.38); transition:all .15s;}
    [data-testid="stBaseButton-primary"]:hover {transform:translateY(-2px); filter:brightness(1.08); color:#fff;}
    [data-testid="stBaseButton-secondary"] {background:#fff; color:#0b1f4d; border:1.5px solid #cbd5e8;
           border-radius:12px; font-weight:600;}
    [data-testid="stBaseButton-secondary"]:hover {border-color:#14b8a6; color:#0f766e;}

    .foot {text-align:center; color:#6b7a90; font-size:0.8rem; margin:34px 0 8px 0; line-height:1.6;}
    </style>""", unsafe_allow_html=True)

def banner():
    chips = "".join(f"<span class='chip'>{c}</span>" for c in
                    ["🛡️ 6 scam red-flag checks", "🗣️ Urdu + English advice", "📷 Reads screenshots", "⚡ Instant, rule-based"])
    st.markdown("<div class='hero'><div class='row'>" + SHIELD + "<h1>Hoshyar</h1></div>"
                "<p class='tag'>Before you click, ask Hoshyar.</p>"
                f"<div class='chips'>{chips}</div>"
                "<p class='note'>Hoshyar flags suspicious patterns; it cannot prove a message is a scam. "
                "When in doubt, contact the real company through its official number.</p></div>",
                unsafe_allow_html=True)

def steps_html():
    items = [("📥", "Add the message", "Upload a screenshot or paste the text"),
             ("🔎", "Agents check it", "Reader, red-flag, risk and advice agents"),
             ("🛡️", "Act safely", "Clear steps and a message for your family")]
    return "<div class='steps'>" + "".join(
        f"<div class='step'><div class='ico'>{i}</div><b>{t}</b><br><span>{d}</span></div>" for i, t, d in items) + "</div>"

def section_title(num, text):
    return f"<div class='sec'><div class='num'>{num}</div><div class='txt'>{text}</div></div>"

def card_html(title, body):
    return f"<div class='card'><h4>{title}</h4>{body}</div>"

SEV = {4: ("CRITICAL", "#d62839"), 3: ("HIGH", "#e8590c"), 2: ("MEDIUM", "#d99a00"), 1: ("INFO", "#1c7ed6")}

def flag_card_html(flags):
    if not flags:
        return "<div class='flag'><span class='pill' style='background:#2e9e5b'>OK</span> No common scam patterns found</div>"
    rows = ""
    for label, pts in sorted(flags, key=lambda x: -x[1]):
        name, color = SEV.get(pts, SEV[1])
        rows += f"<div class='flag'><span class='pill' style='background:{color}'>{name}</span><span>{label}</span></div>"
    return rows

COLORS = {"LOW": "#2e9e5b", "MEDIUM": "#d99a00", "HIGH": "#d62839"}

def gauge_html(level, score):
    strength = min(score, 10) / 10
    theta = math.pi * (1 - strength)
    nx = 100 + 62 * math.cos(theta)
    ny = 100 - 62 * math.sin(theta)
    svg = ("<svg viewBox='0 0 200 120' width='270'>"
           "<path d='M20 100 A80 80 0 0 1 60 30.72' stroke='#2e9e5b' stroke-width='16' fill='none'/>"
           "<path d='M60 30.72 A80 80 0 0 1 140 30.72' stroke='#e0a100' stroke-width='16' fill='none'/>"
           "<path d='M140 30.72 A80 80 0 0 1 180 100' stroke='#d62839' stroke-width='16' fill='none'/>"
           f"<line x1='100' y1='100' x2='{nx:.1f}' y2='{ny:.1f}' stroke='#222' stroke-width='4' stroke-linecap='round'/>"
           "<circle cx='100' cy='100' r='7' fill='#222'/>"
           "<text x='14' y='116' font-size='9' fill='#2e9e5b' font-weight='bold'>LOW</text>"
           "<text x='84' y='20' font-size='9' fill='#b58300' font-weight='bold'>MEDIUM</text>"
           "<text x='166' y='116' font-size='9' fill='#d62839' font-weight='bold'>HIGH</text></svg>")
    c = COLORS[level]
    return (f"<div class='card' style='display:flex;align-items:center;gap:28px;flex-wrap:wrap;border-left-color:{c};'>"
            "<div><div style='font-size:0.9rem;color:#6b7a90;'>Risk level</div>"
            f"<div style='font-size:2.6rem;font-weight:800;color:{c};line-height:1.1;'>{level}</div></div>"
            f"<div>{svg}</div>"
            "<div style='background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:10px 18px;'>"
            "<div style='font-size:0.8rem;color:#6b7a90;'>Warning-sign strength</div>"
            f"<div style='font-size:2rem;font-weight:800;color:{c};'>{int(strength*100)}%</div></div></div>")

def footer_html():
    return ("<div class='foot'>Hoshyar never gives legal or financial certainty. It only flags warning signs.<br>"
            "Built for the Pak Angels Cohort 11 Hackathon · Generative AI + Multi-Agent Workflow</div>")
