"""Look and feel: navy / light-blue styling and the animated header (anime.js)."""
from functools import lru_cache
from pathlib import Path

STATIC = Path(__file__).parent / "static"

NAVY = "#0A1A33"
NAVY_2 = "#12294D"
SKY = "#4FC3F7"
ICE = "#9ED8FF"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, .stApp, .stMarkdown, p, li, h1, h2, h3, h4, label, input, textarea,
.stButton > button, [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {{
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
}}
/* Keep Streamlit's icons on their icon font */
[data-testid="stIconMaterial"], [data-testid="stExpanderIcon"] {{
  font-family: 'Material Symbols Rounded' !important;
}}

/* Page background: deep navy with soft blue glows */
[data-testid="stAppViewContainer"] {{
  background:
    radial-gradient(900px 500px at 85% -10%, rgba(79,195,247,0.16), transparent 60%),
    radial-gradient(700px 400px at -10% 110%, rgba(30,90,180,0.25), transparent 60%),
    {NAVY};
}}
[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 1.2rem; max-width: 1100px; }}

/* Sidebar */
[data-testid="stSidebar"] {{
  background: linear-gradient(180deg, #081428 0%, #0F2547 100%);
  border-right: 1px solid rgba(79,195,247,0.18);
}}
[data-testid="stSidebar"] h2 {{ color: {ICE}; letter-spacing: .02em; }}
[data-testid="stMetric"] {{
  background: rgba(79,195,247,0.08);
  border: 1px solid rgba(79,195,247,0.25);
  border-radius: 14px; padding: 12px 16px;
}}
[data-testid="stMetricValue"] {{ color: {SKY}; font-weight: 800; }}

/* Buttons (example questions, new conversation) */
.stButton > button {{
  background: rgba(18,41,77,0.85);
  color: #D9ECFF;
  border: 1px solid rgba(79,195,247,0.35);
  border-radius: 999px;
  padding: .55rem 1rem;
  transition: transform .15s ease, box-shadow .2s ease, border-color .2s ease, background .2s ease;
}}
.stButton > button:hover {{
  border-color: {SKY};
  background: rgba(79,195,247,0.14);
  color: #FFFFFF;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(79,195,247,0.25);
}}

/* Chat messages as cards */
[data-testid="stChatMessage"] {{
  background: rgba(18,41,77,0.72);
  border: 1px solid rgba(79,195,247,0.16);
  border-radius: 18px;
  padding: 1rem 1.2rem;
  margin-bottom: .9rem;
  box-shadow: 0 10px 30px rgba(0,0,0,0.25);
  animation: rise .45s cubic-bezier(.2,.8,.2,1) both;
}}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{
  background: linear-gradient(135deg, rgba(79,195,247,0.20), rgba(30,90,180,0.22));
  border-color: rgba(79,195,247,0.40);
}}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {{
  border-left: 3px solid {SKY};
}}
[data-testid="stChatMessage"] h1, [data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3 {{ color: {ICE}; }}
[data-testid="stChatMessage"] strong {{ color: #FFFFFF; }}
[data-testid="stChatMessage"] a {{ color: {SKY}; }}
[data-testid="stChatMessage"] table {{ border-radius: 10px; overflow: hidden; }}
[data-testid="stChatMessage"] th {{ background: rgba(79,195,247,0.15); color: {ICE}; }}

@keyframes rise {{ from {{ opacity: 0; transform: translateY(12px); }} to {{ opacity: 1; transform: none; }} }}

/* Sources expander */
[data-testid="stExpander"] {{
  border: 1px solid rgba(79,195,247,0.22) !important;
  border-radius: 12px !important;
  background: rgba(8,20,40,0.55);
}}
[data-testid="stExpander"] summary {{ color: {ICE}; }}

/* Chat input */
[data-testid="stChatInput"] {{
  border: 1px solid rgba(79,195,247,0.45) !important;
  border-radius: 16px !important;
  background: rgba(18,41,77,0.9) !important;
  box-shadow: 0 0 0 4px rgba(79,195,247,0.06);
}}
[data-testid="stChatInput"]:focus-within {{
  border-color: {SKY} !important;
  box-shadow: 0 0 0 4px rgba(79,195,247,0.18);
}}
[data-testid="stBottom"] > div {{ background: transparent; }}

/* Scrollbar */
::-webkit-scrollbar {{ width: 10px; }}
::-webkit-scrollbar-thumb {{ background: rgba(79,195,247,0.25); border-radius: 10px; }}
</style>
"""


@lru_cache(maxsize=1)
def _anime_js() -> str:
    path = STATIC / "anime.umd.min.js"
    return path.read_text(encoding="utf-8") if path.exists() else ""


def header_html(passages: int) -> str:
    """Animated hero banner. Runs inside a Streamlit component iframe."""
    chips = [f"{passages:,} passages", "IRS", "FDIC", "SEC", "SSA", "Live .gov search"]
    chip_html = "".join(f'<span class="chip">{c}</span>' for c in chips)
    title = "AI Financial Advisor"
    letters = "".join(
        f'<span class="ch">{"&nbsp;" if c == " " else c}</span>' for c in title
    )
    return f"""
<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;700;800&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; margin: 0; }}
  body {{ background: transparent; font-family: 'Plus Jakarta Sans', system-ui, sans-serif; overflow: hidden; }}
  .hero {{
    position: relative; height: 196px; border-radius: 22px; overflow: hidden;
    padding: 28px 34px;
    background: linear-gradient(120deg, #0B2147 0%, #12336A 55%, #1A4C8F 100%);
    border: 1px solid rgba(79,195,247,0.30);
    box-shadow: 0 18px 50px rgba(0,0,0,0.35);
  }}
  .orb {{ position: absolute; border-radius: 50%; filter: blur(30px); opacity: .55; }}
  .o1 {{ width: 220px; height: 220px; background: #4FC3F7; right: -40px; top: -80px; }}
  .o2 {{ width: 160px; height: 160px; background: #2F6FD6; right: 220px; bottom: -90px; }}
  svg.chart {{ position: absolute; right: 26px; bottom: 18px; width: 46%; height: 120px; }}
  .content {{ position: relative; z-index: 2; }}
  .eyebrow {{ color: #9ED8FF; font-size: 12px; font-weight: 700; letter-spacing: .18em; text-transform: uppercase; }}
  h1 {{ color: #FFFFFF; font-size: 36px; font-weight: 800; margin: 6px 0 6px; letter-spacing: -.01em; }}
  .ch {{ display: inline-block; }}
  .sub {{ color: #C9E3FF; font-size: 15px; max-width: 520px; }}
  .chips {{ margin-top: 16px; display: flex; gap: 8px; flex-wrap: wrap; }}
  .chip {{
    color: #E6F4FF; font-size: 12px; font-weight: 600; padding: 6px 12px; border-radius: 999px;
    background: rgba(79,195,247,0.16); border: 1px solid rgba(158,216,255,0.40);
  }}
  @media (max-width: 760px) {{ svg.chart {{ opacity: .35; width: 80%; }} h1 {{ font-size: 28px; }} }}
</style></head>
<body>
<div class="hero">
  <div class="orb o1"></div><div class="orb o2"></div>
  <svg class="chart" viewBox="0 0 400 120" preserveAspectRatio="none">
    <defs>
      <linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#9ED8FF" stop-opacity=".2"/><stop offset="1" stop-color="#4FC3F7"/></linearGradient>
      <linearGradient id="fill" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#4FC3F7" stop-opacity=".25"/><stop offset="1" stop-color="#4FC3F7" stop-opacity="0"/></linearGradient>
    </defs>
    <path class="area" d="M0,105 C40,98 60,92 90,90 C130,86 150,70 185,72 C220,74 240,52 275,48 C310,44 335,30 360,22 L400,10 L400,120 L0,120 Z" fill="url(#fill)"/>
    <path class="line" d="M0,105 C40,98 60,92 90,90 C130,86 150,70 185,72 C220,74 240,52 275,48 C310,44 335,30 360,22 L400,10"
          fill="none" stroke="url(#g)" stroke-width="3.5" stroke-linecap="round"/>
    <circle class="dot" cx="90" cy="90" r="4" fill="#9ED8FF"/>
    <circle class="dot" cx="185" cy="72" r="4" fill="#9ED8FF"/>
    <circle class="dot" cx="275" cy="48" r="4" fill="#9ED8FF"/>
    <circle class="dot" cx="400" cy="10" r="5" fill="#4FC3F7"/>
  </svg>
  <div class="content">
    <div class="eyebrow">Personal finance · Taxes · Investing</div>
    <h1>{letters}</h1>
    <div class="sub">Cited answers from official IRS, FDIC, SEC and SSA publications, with this year's numbers checked online.</div>
    <div class="chips">{chip_html}</div>
  </div>
</div>
<script>{_anime_js()}</script>
<script>
  // Everything is visible by default; animations only run if anime.js loaded.
  if (window.anime) {{
    const {{ animate, stagger, createTimeline, svg }} = anime;
    createTimeline({{ defaults: {{ ease: 'outExpo' }} }})
      .add('.eyebrow', {{ opacity: {{ from: 0 }}, y: {{ from: -10 }}, duration: 600 }})
      .add('.ch', {{ opacity: {{ from: 0 }}, y: {{ from: 28 }}, rotate: {{ from: 8 }}, delay: stagger(28), duration: 900 }}, '-=350')
      .add('.sub', {{ opacity: {{ from: 0 }}, y: {{ from: 12 }}, duration: 700 }}, '-=600')
      .add('.chip', {{ opacity: {{ from: 0 }}, scale: {{ from: .8 }}, delay: stagger(70), duration: 600, ease: 'outBack' }}, '-=450')
      .add(svg.createDrawable('.line'), {{ draw: ['0 0', '0 1'], duration: 1600, ease: 'inOutSine' }}, 200)
      .add('.area', {{ opacity: {{ from: 0 }}, duration: 900 }}, '-=900')
      .add('.dot', {{ scale: {{ from: 0 }}, delay: stagger(140), duration: 500, ease: 'outBack' }}, '-=700');
    animate('.o1', {{ x: -30, y: 20, duration: 6000, alternate: true, loop: true, ease: 'inOutSine' }});
    animate('.o2', {{ x: 40, y: -15, duration: 7000, alternate: true, loop: true, ease: 'inOutSine' }});
    animate('.dot:last-of-type', {{ scale: [1, 1.6], opacity: [1, .5], duration: 1100, alternate: true, loop: true, delay: 2200, ease: 'inOutSine' }});
  }}
</script>
</body></html>
"""
