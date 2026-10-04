import os, json, time, re, html
import streamlit as st
from style import inject_css, banner, gauge_html
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODELS = ["gemini-3.8-flash", "gemini-flash-latest"]  # add other names from AI Studio

st.set_page_config(page_title="Hoshyar", page_icon="🛡️")
inject_css()
banner()

def ask_gemini(contents, as_json=True):
    last_error = None
    cfg = types.GenerateContentConfig(response_mime_type="application/json") if as_json else None
    for model in MODELS:
        for attempt in range(2):
            try:
                resp = client.models.generate_content(model=model, contents=contents, config=cfg)
                return json.loads(resp.text) if as_json else resp.text
            except Exception as e:
                last_error = e
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    break
                time.sleep(3)
    raise last_error

# ---- Agent 1: Reader (only used for screenshots) ----
READER_PROMPT = """Read this screenshot of a message (SMS/WhatsApp/email). Return JSON only:
{"text": "full message text exactly as written", "sender": "sender name/number or null",
 "links": ["every link or web address visible"]}"""

def reader_agent(file):
    part = types.Part.from_bytes(data=file.getvalue(), mime_type=file.type)
    return ask_gemini([READER_PROMPT, part])

# ---- Agent 2: Red-flag detector (plain Python, no AI, always consistent) ----
RULES = [
    ("Asks for an OTP, PIN, password or security code", 4,
     r"\b(otp|pin|cvv|password|verification code|security code)\b|او ٹی پی|پن کوڈ|پاسورڈ"),
    ("Asks you to pay or send money (fee, advance, deposit)", 3,
     r"\b(send|transfer|deposit|pay)\b.{0,40}\b(rs\.?|pkr|rupees|amount|fee|charges)\b|"
     r"\b(advance|processing|registration|clearance|customs|delivery) (fee|charges|payment)\b|فیس جمع"),
    ("Promises a prize, grant or reward you did not apply for", 3,
     r"\b(won|winner|lottery|prize|reward|grant|bisp|benazir|ehsaas|inaam|inam|jackpot|lucky draw)\b|انعام|لاٹری"),
    ("Creates false urgency", 2,
     r"\b(urgent|immediately|within \d+ ?(hours?|minutes?|mins?)|last chance|today only|expires?|jaldi|foran|fori)\b|فوری|جلدی|آج ہی"),
    ("Threatens to block, close or take action against you", 2,
     r"\b(blocked|suspended|deactivated|closed|legal action|arrest|fir|sim will be)\b|بلاک|بند کر|گرفتار"),
    ("Offers easy money or a suspicious job/investment", 2,
     r"\b(work from home|earn (rs\.?)?\s?\d+|daily income|part[- ]time job|investment|double your|guaranteed profit)\b"),
]
LINK_RE = (r"(?:https?://|www\.)\S+|\b[\w-]+\.(?:xyz|top|club|link|icu|site|online|click|live)\b\S*|"
           r"\b(?:bit\.ly|tinyurl\.com|cutt\.ly|rb\.gy|is\.gd|t\.co)/\S+")
SHORTENERS = ("bit.ly", "tinyurl.com", "cutt.ly", "rb.gy", "is.gd", "t.co")

def flag_agent(text, links):
    flags = []
    for label, pts, pattern in RULES:
        if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
            flags.append((label, pts))
    all_links = set(links or []) | set(re.findall(LINK_RE, text, re.IGNORECASE))
    if all_links:
        if any(s in l.lower() for l in all_links for s in SHORTENERS):
            flags.append(("Contains a shortened link that hides the real website", 2))
        else:
            flags.append(("Contains a link. Do not click it until you verify the sender", 1))
    return flags, sorted(all_links)

# ---- Agent 3: Risk scorer ----
def risk_agent(flags):
    score = sum(p for _, p in flags)
    if score >= 6:
        return "HIGH", score
    if score >= 3:
        return "MEDIUM", score
    return "LOW", score

# ---- Agent 4: Advice + family message (one AI call, with fallback) ----
FALLBACK = {
    "HIGH": "Do not reply, click any link, or share any code. Contact the real company or bank using the number on its official website or card. Tell a family member.",
    "MEDIUM": "Be careful. Do not click links or share personal details. Verify the sender through an official number first.",
    "LOW": "No strong warning signs were found, but this does not prove the message is safe. Verify the sender before sharing any information.",
}

def advice_agent(text, level, reasons, lang):
    prompt = (f"A message was checked for scam warning signs. Risk level: {level}.\n"
              f"Warning signs found: {reasons}.\nMessage: {text}\n\n"
              f"Write in {lang}. Return JSON only: "
              '{"advice": "3-4 short simple steps for an elderly or first-time smartphone user", '
              '"family_message": "a short calm message to forward to family warning about this message"}. '
              "Never claim certainty that it is or is not a scam. Do not give legal advice. "
              "Tell the person to verify through the company's official number or website.")
    return ask_gemini(prompt)

# ---------------- UI ----------------
from style import flag_card_html, steps_html, footer_html, section_title, card_html, SAMPLES

def as_text(x):
    return "\n".join(map(str, x)) if isinstance(x, list) else str(x)

def load_sample(key):
    st.session_state["msg_text"] = SAMPLES[key]

st.markdown(steps_html(), unsafe_allow_html=True)
st.markdown(section_title("1", "Add the suspicious message"), unsafe_allow_html=True)
st.caption("No message handy? Try a sample:")
b1, b2, b3 = st.columns(3)
b1.button("🎁 Fake grant scam", on_click=load_sample, args=("grant",), use_container_width=True)
b2.button("🏦 Fake bank alert", on_click=load_sample, args=("bank",), use_container_width=True)
b3.button("✅ Normal message", on_click=load_sample, args=("safe",), use_container_width=True)

c1, c2 = st.columns(2)
shot = c1.file_uploader("Upload a screenshot of the message", type=["jpg", "jpeg", "png"])
pasted = c2.text_area("...or paste the message text", height=150, key="msg_text")
lang = st.selectbox("Advice language", ["Urdu", "English"])

st.markdown(section_title("2", "Check it"), unsafe_allow_html=True)
if st.button("✓ Check this message", type="primary", use_container_width=True):
    text, links, sender = pasted.strip(), [], None
    if shot and not text:
        with st.spinner("Reading screenshot..."):
            try:
                r = reader_agent(shot)
                text, links, sender = r.get("text", ""), r.get("links", []), r.get("sender")
            except Exception as e:
                st.error(f"Could not read the screenshot. Paste the text instead. ({e})")
    if not text:
        st.warning("Please upload a screenshot or paste a message.")
        st.stop()

    flags, found_links = flag_agent(text, links)
    level, score = risk_agent(flags)

    st.markdown(section_title("3", "Your safety report"), unsafe_allow_html=True)
    body = "<p style='margin:0'>" + html.escape(text) + "</p>"
    if sender:
        body += "<p style='margin:8px 0 0 0'><b>Sender:</b> " + html.escape(str(sender)) + "</p>"
    if found_links:
        body += "<p style='margin:8px 0 0 0'><b>Links found:</b> " + html.escape(", ".join(found_links)) + "</p>"
    st.markdown(card_html("Message checked", body), unsafe_allow_html=True)
    st.markdown(gauge_html(level, score), unsafe_allow_html=True)
    st.markdown(card_html("Why this result", flag_card_html(flags)), unsafe_allow_html=True)

    try:
        out = advice_agent(text, level, [l for l, _ in flags], lang)
        advice = as_text(out.get("advice", FALLBACK[level]))
        fam = as_text(out.get("family_message", ""))
        st.markdown(card_html("What to do", html.escape(advice).replace("\n", "<br>")), unsafe_allow_html=True)
        st.markdown(section_title("4", "Warn your family"), unsafe_allow_html=True)
        st.text_area("Copy and forward", fam, height=140)
    except Exception:
        st.markdown(card_html("What to do", html.escape(FALLBACK[level])), unsafe_allow_html=True)
        st.info("AI advice is unavailable right now (service busy or daily limit reached). The risk check above still works.")

st.markdown(footer_html(), unsafe_allow_html=True)
