"""Look and feel.

Type system (two families, clearly distinct):
  - Newsreader (serif): headings, the app title and the greeting.
  - Public Sans: everything else. It's the U.S. government's own typeface
    (USWDS), a quiet nod to the IRS/FDIC/SEC/SSA sources the app is built on.
Motion: one moment only, the header chart drawing in on load.
"""
from functools import lru_cache
from pathlib import Path

STATIC = Path(__file__).parent / "static"

NAVY = "#0A1A33"      # page
NAVY_2 = "#12294D"    # cards, inputs
LINE = "#24406E"      # borders
SKY = "#4FC3F7"       # accent (links, focus, chart)
ICE = "#9ED8FF"       # secondary accent (headings)
TEXT = "#E6F0FF"
MUTED = "#A9BEDC"

FONTS_URL = (
    "https://fonts.googleapis.com/css2?"
    "family=Newsreader:opsz,wght@6..72,500;6..72,600"
    "&family=Public+Sans:wght@400;500;600;700&display=swap"
)
SERIF = "'Newsreader', Georgia, 'Times New Roman', serif"
SANS = "'Public Sans', -apple-system, 'Segoe UI', system-ui, sans-serif"

CSS = f"""
<style>
@import url('{FONTS_URL}');

/* ---- Type ------------------------------------------------------------ */
html, body, .stApp, .stMarkdown, p, li, td, th, label, input, textarea,
.stButton > button, [data-testid="stMetricLabel"], [data-testid="stCaptionContainer"] {{
  font-family: {SANS};
}}
.stMarkdown p, .stMarkdown li {{ font-size: 1rem; line-height: 1.65; }}
.stMarkdown, .stMarkdown p {{ max-width: 72ch; }}

h1, h2, h3, h4,
[data-testid="stHeading"] *, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {{
  font-family: {SERIF} !important;
  font-weight: 600 !important;
  letter-spacing: -0.005em;
  color: {ICE};
}}
.stMarkdown h1 {{ font-size: 1.75rem !important; }}
.stMarkdown h2 {{ font-size: 1.45rem !important; margin-top: 1.4rem; }}
.stMarkdown h3 {{ font-size: 1.2rem !important; margin-top: 1.1rem; }}
.stMarkdown strong {{ color: #FFFFFF; font-weight: 600; }}
.stMarkdown a {{ color: {SKY}; text-underline-offset: 3px; }}

[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {{
  font-size: .82rem !important; line-height: 1.5; color: {MUTED};
}}

/* Keep Streamlit's icons on their icon font */
[data-testid="stIconMaterial"], [data-testid="stExpanderIcon"] {{
  font-family: 'Material Symbols Rounded' !important;
}}

/* ---- Surfaces -------------------------------------------------------- */
[data-testid="stAppViewContainer"] {{ background: {NAVY}; }}
[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 1.2rem; max-width: 980px; }}

[data-testid="stSidebar"] {{ background: #081530; border-right: 1px solid {LINE}; }}
[data-testid="stSidebar"] h2 {{ font-size: 1.3rem !important; }}
[data-testid="stMetric"] {{
  border: 1px solid {LINE}; border-radius: 10px; padding: 12px 14px; background: {NAVY_2};
}}
[data-testid="stMetricValue"] {{
  font-family: {SANS}; font-weight: 600; color: {TEXT};
  font-variant-numeric: tabular-nums;
}}

/* ---- Buttons --------------------------------------------------------- */
.stButton > button {{
  background: transparent; color: {TEXT};
  border: 1px solid {LINE}; border-radius: 8px;
  font-weight: 500; font-size: .92rem; padding: .6rem .9rem; text-align: left;
  transition: border-color .15s ease, background .15s ease;
}}
.stButton > button:hover {{ border-color: {SKY}; background: rgba(79,195,247,0.08); color: #FFFFFF; }}
.stButton > button:focus-visible {{ outline: 2px solid {SKY}; outline-offset: 2px; }}

/* ---- Chat ------------------------------------------------------------ */
[data-testid="stChatMessage"] {{
  background: transparent; border: 0; border-radius: 0;
  padding: 1.1rem 0; margin: 0; border-bottom: 1px solid rgba(36,64,110,0.6);
}}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) .stMarkdown p {{
  font-weight: 500; color: #FFFFFF;
}}
[data-testid="stChatMessage"] table {{ border-collapse: collapse; font-variant-numeric: tabular-nums; }}
[data-testid="stChatMessage"] th {{ background: {NAVY_2}; color: {ICE}; font-weight: 600; }}
[data-testid="stChatMessage"] th, [data-testid="stChatMessage"] td {{ border: 1px solid {LINE}; }}

[data-testid="stExpander"] {{
  border: 1px solid {LINE} !important; border-radius: 8px !important; background: transparent;
}}
[data-testid="stExpander"] summary p {{ font-size: .9rem; color: {MUTED}; }}

/* ---- Input ----------------------------------------------------------- */
[data-testid="stBottom"] > div {{ background: {NAVY}; }}
[data-testid="stChatInput"] {{
  border: 1px solid {LINE} !important; border-radius: 12px !important; background: {NAVY_2} !important;
}}
[data-testid="stChatInput"]:focus-within {{ border-color: {SKY} !important; }}
[data-testid="stChatInput"] textarea {{
  min-height: 64px !important; font-size: 1.02rem !important;
  padding: 1.1rem 1rem !important; line-height: 1.5 !important;
}}

@media (prefers-reduced-motion: reduce) {{ * {{ transition: none !important; }} }}
</style>
"""


@lru_cache(maxsize=1)
def _anime_js() -> str:
    path = STATIC / "anime.umd.min.js"
    return path.read_text(encoding="utf-8") if path.exists() else ""


def header_html(passages: int) -> str:
    """Header with a line chart that draws itself once on load (anime.js)."""
    return f"""
<!doctype html><html><head><meta charset="utf-8">
<link href="{FONTS_URL}" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; margin: 0; }}
  body {{ background: transparent; font-family: {SANS}; overflow: hidden; padding: 2px; }}
  .hero {{
    position: relative; min-height: 176px; overflow: hidden;
    padding: 30px 34px; border-radius: 14px;
    background: {NAVY_2}; border: 1px solid {LINE};
  }}
  svg.chart {{ position: absolute; right: 0; bottom: 0; width: 52%; height: 100%; }}
  .content {{ position: relative; z-index: 2; max-width: 30rem; }}
  h1 {{ font-family: {SERIF}; font-weight: 600; font-size: 40px; line-height: 1.05; color: #FFFFFF; letter-spacing: -0.01em; }}
  .sub {{ margin-top: 12px; color: {MUTED}; font-size: 15px; line-height: 1.55; }}
  .sub b {{ color: {TEXT}; font-weight: 600; font-variant-numeric: tabular-nums; }}
  @media (max-width: 760px) {{ svg.chart {{ opacity: .3; width: 90%; }} h1 {{ font-size: 32px; }} }}
  @media (max-width: 480px) {{ .hero {{ padding: 22px; }} h1 {{ font-size: 27px; }} .sub {{ font-size: 14px; }} }}
</style></head>
<body>
<div class="hero">
  <svg class="chart" viewBox="0 0 400 176" preserveAspectRatio="none" aria-hidden="true">
    <defs>
      <linearGradient id="fill" x1="0" x2="0" y1="0" y2="1">
        <stop offset="0" stop-color="{SKY}" stop-opacity=".18"/><stop offset="1" stop-color="{SKY}" stop-opacity="0"/>
      </linearGradient>
    </defs>
    <g stroke="{LINE}" stroke-width="1">
      <line x1="0" y1="44" x2="400" y2="44"/><line x1="0" y1="88" x2="400" y2="88"/><line x1="0" y1="132" x2="400" y2="132"/>
    </g>
    <path class="area" d="M0,150 C50,146 80,138 120,132 C165,125 190,112 230,108 C270,104 300,80 335,70 C360,62 380,48 400,36 L400,176 L0,176 Z" fill="url(#fill)"/>
    <path class="line" d="M0,150 C50,146 80,138 120,132 C165,125 190,112 230,108 C270,104 300,80 335,70 C360,62 380,48 400,36"
          fill="none" stroke="{SKY}" stroke-width="2.5" stroke-linecap="round"/>
  </svg>
  <div class="content">
    <h1>AI Financial Advisor</h1>
    <p class="sub">Answers grounded in <b>{passages:,}</b> passages from IRS, FDIC, SEC and Social Security publications, with this year's limits checked online.</p>
  </div>
</div>
<script>{_anime_js()}</script>
<script>
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (window.anime && !reduce) {{
    const {{ createTimeline, svg }} = anime;
    createTimeline()
      .add(svg.createDrawable('.line'), {{ draw: ['0 0', '0 1'], duration: 1800, ease: 'inOutQuad' }}, 150)
      .add('.area', {{ opacity: {{ from: 0 }}, duration: 900, ease: 'outQuad' }}, 900);
  }}
</script>
</body></html>
"""


def greeting_html() -> str:
    """Time-of-day greeting before the first question. Uses the viewer's local
    clock (a server on AWS would be in UTC)."""
    return f"""
<!doctype html><html><head><meta charset="utf-8">
<link href="{FONTS_URL}" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; margin: 0; }}
  body {{ background: transparent; overflow: hidden; height: 100vh;
         display: flex; flex-direction: column; justify-content: center; padding: 0 2px; }}
  h2 {{ font-family: {SERIF}; font-weight: 500; font-size: 34px; color: #FFFFFF; letter-spacing: -0.01em; }}
  p {{ font-family: {SANS}; color: {MUTED}; font-size: 16px; margin-top: 8px; }}
  @media (max-width: 480px) {{ h2 {{ font-size: 27px; }} p {{ font-size: 15px; }} }}
</style></head>
<body>
  <h2 id="hello">Hello.</h2>
  <p>Ask about budgeting, debt, saving, investing, retirement accounts or U.S. taxes.</p>
<script>
  const h = new Date().getHours();
  document.getElementById('hello').textContent =
    h < 5 ? 'Working late? How can I help?' : h < 12 ? 'Good morning. How can I help?'
    : h < 17 ? 'Good afternoon. How can I help?' : 'Good evening. How can I help?';
</script>
</body></html>
"""