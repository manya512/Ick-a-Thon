"""Global CSS recreating the Stitch look (cream, matcha, lilac, charcoal; Quicksand + DM Sans).

Fonts load from Google Fonts, so they need an internet connection. Offline, the app falls
back to system sans-serif fonts and still works.
"""
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,700;1,9..40,400&family=Quicksand:wght@500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

:root {
  --cream: #FBF6EC; --cream-2: #F3EBDD; --card: #FFFFFF;
  --matcha: #8C9F32; --matcha-deep: #566500; --matcha-soft: #D7ED76;
  --lilac: #B9A7FF; --lilac-soft: #E7DEFF; --lilac-deep: #493888;
  --ink: #201A19; --ink-2: #362F2E; --muted: #464838;
  --danger: #BA1A1A; --danger-soft: #FFDAD6;
}
html, body, [class*="st-"], .stApp, input, textarea, button, select { font-family: 'DM Sans', system-ui, sans-serif; }
.stApp { background: var(--cream); color: var(--ink); }
header[data-testid="stHeader"], footer, #MainMenu, [data-testid="stToolbar"] { display: none !important; }
.block-container { max-width: 560px !important; padding: 1rem 1rem 7.5rem 1rem !important; }
h1, h2, h3, .lt-display { font-family: 'Quicksand', 'DM Sans', sans-serif !important; font-weight: 700 !important; color: var(--ink); letter-spacing: -0.01em; }

/* Brand bar */
.lt-top { display:flex; align-items:center; justify-content:space-between; gap:8px; padding: 4px 0 14px; }
.lt-brand { display:flex; align-items:center; gap:10px; min-width:0; }
.lt-logo { width:36px; height:36px; border-radius:50%; background: var(--lilac-soft); display:flex; align-items:center; justify-content:center; font-size:19px; }
.lt-brand-name { font-family:'Quicksand',sans-serif; font-weight:700; font-size:20px; line-height:1; color: var(--ink); }
.lt-brand-sub { font-size:11px; font-weight:700; letter-spacing:.04em; color: var(--muted); margin-top:3px; }
.lt-fresh { display:inline-flex; align-items:center; gap:6px; padding:5px 11px; border-radius:999px; background: var(--lilac-soft); color:#1E035D; font-size:11px; font-weight:700; }
.lt-dot { width:8px; height:8px; border-radius:50%; background: var(--matcha); display:inline-block; }
.lt-dot.alert { background: var(--danger); animation: lt-pulse 1.6s ease-in-out infinite; }
@keyframes lt-pulse { 0%,100% { opacity:1 } 50% { opacity:.35 } }
@media (prefers-reduced-motion: reduce) { .lt-dot.alert { animation: none; } }

/* Hero */
.lt-hero-title { font-family:'Quicksand',sans-serif; font-weight:700; font-size:26px; line-height:32px; margin:0; color:var(--ink); }
.lt-hero-sub { font-size:14px; color: var(--muted); margin: 2px 0 10px; }
.lt-banner { background: var(--cream-2); border-radius: 28px; padding: 16px; margin-bottom: 14px; display:flex; justify-content:space-between; gap:12px; align-items:flex-start; }
.lt-pill { display:inline-block; padding:3px 10px; border-radius:999px; background: var(--lilac-soft); color:#1E035D; font-size:11px; font-weight:700; }
.lt-orb { width:46px; height:46px; flex:none; border-radius:50%; background: var(--lilac); display:flex; align-items:center; justify-content:center; font-size:22px; }

/* Stat cards */
.lt-grid { display:grid; grid-template-columns: 1fr 1fr; gap:12px; margin: 6px 0 14px; }
.lt-stat { border-radius: 28px; padding: 14px; background: var(--card); box-shadow: 0 1px 3px rgba(32,26,25,.07); min-height: 96px; display:flex; flex-direction:column; justify-content:space-between; position:relative; overflow:hidden; }
.lt-stat .lbl { font-size:11px; font-weight:700; letter-spacing:.04em; color: var(--muted); }
.lt-stat .num { font-family:'Quicksand',sans-serif; font-weight:700; font-size:34px; line-height:1; margin-top:8px; }
.lt-stat .sub { font-size:13px; font-weight:500; margin-top:3px; color: var(--muted); }
.lt-stat.soon { background: var(--lilac-soft); color:#1E035D; } .lt-stat.soon .lbl, .lt-stat.soon .sub { color:#4B3989; }
.lt-stat.ick { background: var(--ink-2); color:#FBEEEC; } .lt-stat.ick .lbl, .lt-stat.ick .sub { color: #BCD05E; }
.lt-stat.fresh { background:#FEF1EF; } .lt-stat.fresh .num { color: var(--matcha-deep); } .lt-stat.fresh .lbl { color:#404C00; }
.lt-stat .ghost { position:absolute; right:-4px; bottom:-10px; font-size:54px; opacity:.14; }

/* Section cards */
.lt-card { background: var(--card); border-radius: 28px; padding: 16px; box-shadow: 0 1px 3px rgba(32,26,25,.07); margin-bottom: 12px; }
.lt-card-title { font-family:'Quicksand',sans-serif; font-weight:600; font-size:20px; margin:0; }
.lt-bar { display:flex; width:100%; height:12px; border-radius:999px; overflow:hidden; background: var(--cream-2); margin: 12px 0 8px; }
.lt-legend { display:flex; justify-content:space-between; gap:6px; font-size:11px; font-weight:700; color: var(--muted); flex-wrap:wrap; }
.lt-section-head { display:flex; align-items:center; justify-content:space-between; margin: 18px 4px 8px; gap:8px; }
.lt-section-head h2 { font-size: 20px !important; margin:0 !important; padding:0 !important; }
.lt-count { padding:3px 10px; border-radius:999px; font-size:11px; font-weight:700; }
.lt-count.ick { background: var(--danger-soft); color:#93000A; } .lt-count.soon { background: var(--lilac-soft); color:#1E035D; } .lt-count.fresh { background: var(--matcha-soft); color:#181E00; }

/* Product rows */
.lt-item { display:flex; align-items:center; justify-content:space-between; gap:12px; background: var(--card); border-radius: 28px; padding: 12px 14px; box-shadow: 0 1px 3px rgba(32,26,25,.07); }
.lt-item.ick { background: var(--ink-2); color:#FBEEEC; }
.lt-item .left { display:flex; align-items:center; gap:12px; min-width:0; }
.lt-avatar { width:48px; height:48px; flex:none; border-radius:18px; display:flex; align-items:center; justify-content:center; font-size:22px; background: var(--cream-2); }
.lt-item.ick .lt-avatar { background: rgba(255,218,214,.18); }
.lt-name { font-weight:600; font-size:17px; line-height:22px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.lt-meta { font-size:12px; color: var(--muted); font-weight:500; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.lt-item.ick .lt-meta { color:#ECE0DE; }
.lt-badge { flex:none; padding:5px 11px; border-radius:999px; font-size:11px; font-weight:700; white-space:nowrap; }
.lt-badge.ick { background: var(--danger); color:#fff; } .lt-badge.soon { background: var(--lilac); color:#1E035D; } .lt-badge.fresh { background: var(--matcha-soft); color:#404C00; }
.lt-demo { display:inline-block; margin-left:6px; padding:1px 7px; border-radius:999px; background: var(--lilac-soft); color:#4B3989; font-size:10px; font-weight:700; vertical-align:middle; }

/* Empty state / tips / notes */
.lt-empty { text-align:center; background: var(--cream-2); border-radius: 36px; padding: 32px 20px; margin: 10px 0; }
.lt-empty .big { font-size:46px; } .lt-empty h3 { margin: 8px 0 4px !important; font-size:22px !important; }
.lt-empty p { color: var(--muted); font-size:14px; margin:0; }
.lt-tip { display:flex; gap:12px; align-items:center; background:#FEF1EF; border-radius:36px; padding:14px 16px; margin: 14px 0 8px; }
.lt-tip .e { font-size:30px; } .lt-tip b { font-family:'Quicksand',sans-serif; font-size:18px; display:block; }
.lt-micro { text-align:center; background: #F2E5E3; border-radius:999px; padding:10px 16px; font-size:13px; font-weight:500; color: var(--muted); margin: 14px 0 4px; }
.lt-note { display:flex; gap:10px; background: var(--cream-2); border-radius: 24px; padding: 12px 14px; font-size:13px; color: var(--muted); margin-top: 14px; }
.lt-soon-card { display:flex; align-items:center; gap:12px; background: rgba(231,222,255,.55); border-radius:24px; padding:12px 14px; margin: 4px 0 8px; }
.lt-soon-card .t { font-weight:600; font-size:16px; } .lt-soon-card .d { font-size:13px; color:#4B3989; }
.lt-chipnote { font-size:11px; font-weight:700; padding:2px 8px; border-radius:6px; background: var(--lilac); color:#1E035D; }

/* Streamlit widgets -> Stitch styling */
.stButton > button, .stDownloadButton > button { border-radius: 999px; font-weight: 700; font-size: 13px; border: none; background: var(--cream-2); color: var(--ink); padding: .35rem 1rem; min-height: 38px; transition: transform .1s; }
.stButton > button:hover { background: #ECE0DE; color: var(--ink); }
.stButton > button:active { transform: scale(.96); }
.stButton > button[kind="primary"] { background: var(--matcha); color: #2A3200; box-shadow: 0 2px 6px rgba(32,26,25,.15); }
.stButton > button[kind="primary"]:hover { background: #7D8F2B; color:#2A3200; }
.stTextInput input, .stTextArea textarea, .stDateInput input, .stNumberInput input { background: #fff !important; border-radius: 22px !important; border: 1px solid transparent !important; box-shadow: 0 1px 3px rgba(32,26,25,.07); }
.stTextInput > div > div, .stDateInput > div > div, .stNumberInput > div > div, .stSelectbox > div > div { border-radius: 22px !important; }
.stTextInput input:focus, .stTextArea textarea:focus { box-shadow: 0 0 0 2px rgba(99,82,163,.4) !important; }
[data-testid="stWidgetLabel"] p { font-weight:600; font-size:15px; color: var(--ink); }
[data-testid="stPills"] button, [data-testid="stSegmentedControl"] button { border-radius: 999px !important; }
div[data-testid="stAlert"] { border-radius: 22px; }
[data-testid="stDialog"] > div, div[role="dialog"] { border-radius: 32px !important; }

/* Bottom nav (st.container(key="nav")) */
.st-key-nav { position: fixed; bottom: 0; left: 0; right: 0; z-index: 999; background: rgba(251,246,236,.92); backdrop-filter: blur(14px); box-shadow: 0 -2px 12px rgba(32,26,25,.08); padding: 6px 10px calc(8px + env(safe-area-inset-bottom, 0px)); }
.st-key-nav > div { max-width: 560px; margin: 0 auto; }
.st-key-nav [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; gap: 4px !important; align-items: center; }
.st-key-nav [data-testid="stColumn"] { min-width: 0 !important; flex: 1 1 0 !important; width: auto !important; }
.st-key-nav .stButton > button { background: transparent; box-shadow:none; font-size: 11px; padding: .2rem .1rem; min-height: 52px; border-radius: 22px; color: var(--muted); flex-direction: column; gap: 0; width:100%; }
.st-key-nav .stButton > button p { font-size: 11px; font-weight: 700; margin:0; }
.st-key-nav .stButton > button[kind="primary"] { background: rgba(140,159,50,.18); color: var(--matcha-deep); box-shadow:none; }
.st-key-nav .st-key-nav_add button { background: var(--matcha) !important; color:#2A3200 !important; width: 52px; height: 52px; min-height:52px; border-radius: 50% !important; box-shadow: 2px 3px 0 var(--ink) !important; margin: 0 auto; display:flex; }
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
