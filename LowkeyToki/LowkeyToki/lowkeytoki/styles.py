"""Global CSS implementing the Stitch design system exactly.

Tokens are taken verbatim from the exported Tailwind config:
  primary=#566500, primary-container=#8C9F32, primary-fixed=#D7ED76
  secondary=#6352A3, secondary-container=#B9A7FF, secondary-fixed=#E7DEFF
  surface=#FFF8F6, inverse-surface=#362F2E, error=#BA1A1A

Fonts: Quicksand (700) for brand / headings, DM Sans for everything else.
Material Symbols Outlined for iconography (matches Stitch icon usage).
"""
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,700;1,9..40,400&family=Quicksand:wght@500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

/* ── Design tokens (Stitch Tailwind config, verbatim) ─────────────────── */
:root {
  /* Primary – matcha green */
  --primary:                   #566500;
  --primary-container:         #8C9F32;
  --primary-fixed:             #D7ED76;
  --primary-fixed-dim:         #BCD05E;
  --on-primary:                #ffffff;
  --on-primary-container:      #2A3200;
  --on-primary-fixed:          #181E00;
  --on-primary-fixed-variant:  #404C00;
  --inverse-primary:           #BCD05E;

  /* Secondary – lilac */
  --secondary:                 #6352A3;
  --secondary-container:       #B9A7FF;
  --secondary-fixed:           #E7DEFF;
  --secondary-fixed-dim:       #CCBEFF;
  --on-secondary:              #ffffff;
  --on-secondary-container:    #493888;
  --on-secondary-fixed:        #1E035D;
  --on-secondary-fixed-variant:#4B3989;

  /* Surface */
  --surface:                   #FFF8F6;
  --surface-container-lowest:  #FFFFFF;
  --surface-container-low:     #FEF1EF;
  --surface-container:         #F8EBE9;
  --surface-container-high:    #F2E5E3;
  --surface-container-highest: #ECE0DE;
  --surface-variant:           #ECE0DE;
  --surface-dim:               #E4D7D5;

  /* On-surface */
  --on-surface:                #201A19;
  --on-surface-variant:        #464838;
  --on-background:             #201A19;

  /* Inverse */
  --inverse-surface:           #362F2E;
  --inverse-on-surface:        #FBEEEC;

  /* Error */
  --error:                     #BA1A1A;
  --error-container:           #FFDAD6;
  --on-error:                  #ffffff;
  --on-error-container:        #93000A;

  /* Outline */
  --outline:                   #777966;
  --outline-variant:           #C7C8B3;

  /* Tertiary */
  --tertiary:                  #5F5F59;
  --tertiary-container:        #989790;
  --tertiary-fixed:            #E4E3DB;
  --on-tertiary:               #ffffff;

  /* Legacy aliases (kept so nothing breaks) */
  --cream:        var(--surface);
  --cream-2:      var(--surface-container-low);
  --card:         var(--surface-container-lowest);
  --matcha:       var(--primary-container);
  --matcha-deep:  var(--primary);
  --matcha-soft:  var(--primary-fixed);
  --lilac:        var(--secondary-container);
  --lilac-soft:   var(--secondary-fixed);
  --lilac-deep:   var(--secondary);
  --ink:          var(--on-surface);
  --ink-2:        var(--inverse-surface);
  --muted:        var(--on-surface-variant);
  --danger:       var(--error);
  --danger-soft:  var(--error-container);
}

/* ── Base ──────────────────────────────────────────────────────────────── */
html, body, [class*="st-"], .stApp, input, textarea, button, select {
  font-family: 'DM Sans', system-ui, sans-serif;
}
.stApp { background: var(--surface); color: var(--on-surface); }
header[data-testid="stHeader"], footer, #MainMenu,
[data-testid="stToolbar"] { display: none !important; }
.block-container {
  max-width: 560px !important;
  padding: 1rem 1rem 7.5rem 1rem !important;
}
h1, h2, h3, .lt-display {
  font-family: 'Quicksand', 'DM Sans', sans-serif !important;
  font-weight: 700 !important;
  color: var(--on-surface);
  letter-spacing: -0.01em;
}

/* Material Symbols icon baseline */
.material-symbols-outlined {
  font-family: 'Material Symbols Outlined';
  font-weight: normal; font-style: normal;
  line-height: 1; letter-spacing: normal;
  text-transform: none; display: inline-block;
  white-space: nowrap; direction: ltr;
  -webkit-font-smoothing: antialiased;
  vertical-align: middle;
}

/* ── Top bar ───────────────────────────────────────────────────────────── */
.lt-top {
  display: flex; align-items: center;
  justify-content: space-between;
  gap: 8px; padding: 4px 0 14px;
}
.lt-brand { display: flex; align-items: center; gap: 10px; min-width: 0; }
.lt-logo {
  width: 36px; height: 36px; border-radius: 50%;
  background: var(--secondary-fixed);
  display: flex; align-items: center; justify-content: center;
  font-size: 19px;
}
.lt-brand-name {
  font-family: 'Quicksand', sans-serif;
  font-weight: 700; font-size: 20px; line-height: 1;
  color: var(--on-surface);
}
.lt-brand-sub {
  font-size: 11px; font-weight: 700; letter-spacing: .04em;
  color: var(--on-surface-variant); margin-top: 3px;
}
.lt-fresh {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 5px 12px; border-radius: 999px;
  background: var(--secondary-fixed);
  color: var(--on-secondary-fixed);
  font-size: 11px; font-weight: 700;
}
.lt-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--primary-container); display: inline-block;
}
.lt-dot.alert {
  background: var(--error);
  animation: lt-pulse 1.6s ease-in-out infinite;
}
@keyframes lt-pulse { 0%,100%{opacity:1} 50%{opacity:.35} }
@media (prefers-reduced-motion:reduce) { .lt-dot.alert { animation:none; } }

/* ── Hero section ─────────────────────────────────────────────────────── */
.lt-hero-title {
  font-family: 'Quicksand', sans-serif;
  font-weight: 700; font-size: 26px; line-height: 32px;
  margin: 0; color: var(--on-surface);
}
.lt-hero-sub { font-size: 14px; color: var(--on-surface-variant); margin: 2px 0 10px; }

/* Banner card (Add page, Use First page) */
.lt-banner {
  background: var(--surface-container-high);
  border-radius: 2rem; padding: 16px; margin-bottom: 14px;
  display: flex; justify-content: space-between;
  gap: 12px; align-items: flex-start;
}
.lt-pill {
  display: inline-flex; align-items: center;
  padding: 3px 10px; border-radius: 999px;
  background: var(--secondary-container);
  color: var(--on-secondary-container);
  font-size: 11px; font-weight: 700;
}
.lt-live-badge {
  display: inline-flex; align-items: center;
  padding: 2px 8px; border-radius: 999px;
  background: var(--surface-container);
  color: var(--on-surface-variant);
  font-size: 11px; font-weight: 700;
}
.lt-orb {
  width: 46px; height: 46px; flex: none; border-radius: 50%;
  background: var(--secondary-container);
  color: var(--on-secondary-container);
  display: flex; align-items: center; justify-content: center;
  font-size: 22px;
}

/* ── Stat cards 2×2 grid ───────────────────────────────────────────────── */
.lt-grid {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 12px; margin: 6px 0 14px;
}
.lt-stat {
  border-radius: 1rem; padding: 14px;
  background: var(--surface-container-lowest);
  box-shadow: 0 1px 4px rgba(32,26,25,.08);
  min-height: 108px;
  display: flex; flex-direction: column;
  justify-content: space-between;
  position: relative; overflow: hidden;
}
/* Header row inside stat card */
.lt-stat-head {
  display: flex; align-items: center;
  justify-content: space-between; gap: 8px;
}
.lt-stat-lbl {
  font-size: 11px; font-weight: 700; letter-spacing: .04em;
  color: var(--on-surface-variant);
}
.lt-stat-icon {
  width: 28px; height: 28px; border-radius: 50%; flex-shrink: 0;
  background: var(--surface-container);
  display: flex; align-items: center; justify-content: center;
}
.lt-stat-icon .material-symbols-outlined { font-size: 15px; color: var(--on-surface); }
.lt-stat-icon.s-soon  { background: var(--secondary-container); }
.lt-stat-icon.s-soon  .material-symbols-outlined { color: var(--on-secondary-container); }
.lt-stat-icon.s-ick   { background: var(--error); animation: lt-pulse 1.6s ease-in-out infinite; }
.lt-stat-icon.s-ick   .material-symbols-outlined { color: var(--on-error); }
.lt-stat-icon.s-fresh { background: var(--primary-fixed); }
.lt-stat-icon.s-fresh .material-symbols-outlined { color: var(--on-primary-fixed); }
/* Number + sub */
.lt-stat-num {
  font-family: 'Quicksand', sans-serif;
  font-weight: 700; font-size: 32px; line-height: 1;
  margin-top: 8px; color: var(--on-surface);
}
.lt-stat-sub { font-size: 13px; font-weight: 500; margin-top: 3px; color: var(--on-surface-variant); }
/* Variant themes */
.lt-stat.soon { background: var(--secondary-fixed); }
.lt-stat.soon .lt-stat-lbl  { color: var(--on-secondary-fixed-variant); }
.lt-stat.soon .lt-stat-num  { color: var(--on-secondary-fixed); }
.lt-stat.soon .lt-stat-sub  { color: var(--on-secondary-fixed-variant); }

.lt-stat.ick  { background: var(--inverse-surface); }
.lt-stat.ick  .lt-stat-lbl  { color: var(--primary-fixed-dim); }
.lt-stat.ick  .lt-stat-num  { color: var(--inverse-on-surface); }
.lt-stat.ick  .lt-stat-sub  { color: var(--primary-fixed); }
.lt-stat.ick  .ghost {
  position: absolute; right: -4px; bottom: -10px;
  font-size: 54px; opacity: .14; pointer-events: none;
}
.lt-stat.fresh { background: var(--surface-container-low); }
.lt-stat.fresh .lt-stat-lbl { color: var(--on-primary-fixed-variant); }
.lt-stat.fresh .lt-stat-num { color: var(--primary); }
.lt-stat.fresh .lt-stat-sub { color: var(--on-surface-variant); }

/* ── Shelf Health Pulse card ───────────────────────────────────────────── */
.lt-card {
  background: var(--surface-container-lowest);
  border-radius: 1rem; padding: 16px;
  box-shadow: 0 1px 4px rgba(32,26,25,.08);
  margin-bottom: 12px;
}
.lt-card-title {
  font-family: 'Quicksand', sans-serif;
  font-weight: 600; font-size: 20px; margin: 0;
}
.lt-bar {
  display: flex; width: 100%; height: 12px;
  border-radius: 999px; overflow: hidden;
  background: var(--surface-container);
  margin: 12px 0 8px;
}
.lt-legend {
  display: flex; justify-content: space-between; gap: 6px;
  font-size: 11px; font-weight: 700;
  color: var(--on-surface-variant); flex-wrap: wrap;
}

/* ── Section heads ─────────────────────────────────────────────────────── */
.lt-section-head {
  display: flex; align-items: center;
  justify-content: space-between;
  margin: 18px 0 8px; gap: 8px;
}
.lt-section-head h2 { font-size: 20px !important; margin: 0 !important; padding: 0 !important; }
.lt-count {
  padding: 4px 12px; border-radius: 999px;
  font-size: 11px; font-weight: 700;
}
.lt-count.ick   { background: var(--error-container);   color: var(--on-error-container); }
.lt-count.soon  { background: var(--secondary-fixed);   color: var(--on-secondary-fixed); }
.lt-count.fresh { background: var(--primary-fixed);     color: var(--on-primary-fixed-variant); }

/* ── Product rows ──────────────────────────────────────────────────────── */
.lt-item {
  display: flex; align-items: center;
  gap: 12px;
  background: var(--surface-container-lowest);
  border-radius: 1rem;
  padding: 12px 14px;
  box-shadow: 0 1px 4px rgba(32,26,25,.08);
  margin-bottom: 4px;
}
.lt-item.ick { background: var(--inverse-surface); }
.lt-item .left { display: flex; align-items: center; gap: 12px; min-width: 0; flex: 1; }

/* Avatar circle – category icon */
.lt-avatar {
  width: 48px; height: 48px; flex: none;
  border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  background: var(--surface-container);
  font-size: 22px;
}
.lt-avatar .material-symbols-outlined { font-size: 22px; color: var(--on-surface-variant); }
/* Status-tinted avatars */
.lt-av-ick   { background: var(--error-container); }
.lt-av-ick   .material-symbols-outlined { color: var(--on-error-container); }
.lt-av-soon  { background: var(--secondary-fixed); }
.lt-av-soon  .material-symbols-outlined { color: var(--on-secondary-container); }
.lt-av-fresh { background: var(--primary-fixed); }
.lt-av-fresh .material-symbols-outlined { color: var(--on-primary-fixed); }

.lt-name {
  font-weight: 600; font-size: 17px; line-height: 22px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  color: var(--on-surface);
}
.lt-item.ick .lt-name { color: var(--inverse-on-surface); }

/* Meta row: category pill + status badge, inline */
.lt-meta-row {
  display: flex; align-items: center;
  gap: 6px; flex-wrap: wrap; margin-top: 3px;
}
.lt-meta {
  font-size: 12px; color: var(--on-surface-variant);
  font-weight: 500;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.lt-item.ick .lt-meta { color: #ECE0DE; }

.lt-expiry-line {
  font-size: 12px; font-weight: 700;
  color: var(--on-surface-variant);
  margin-top: 2px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.lt-item.ick .lt-expiry-line { color: #D0C4C2; }

/* Status badges */
.lt-badge {
  flex: none; padding: 3px 10px; border-radius: 999px;
  font-size: 11px; font-weight: 700; white-space: nowrap;
}
.lt-badge.ick   { background: var(--inverse-surface);     color: var(--inverse-on-surface); }
.lt-badge.soon  { background: var(--secondary-container); color: var(--on-secondary-container); }
.lt-badge.fresh { background: var(--primary-fixed);       color: var(--on-primary-fixed-variant); }

/* DEMO label */
.lt-demo {
  display: inline-block; margin-left: 6px;
  padding: 1px 7px; border-radius: 999px;
  background: var(--secondary-fixed);
  color: var(--on-secondary-fixed);
  font-size: 10px; font-weight: 700;
  vertical-align: middle;
}

/* ── Empty states ──────────────────────────────────────────────────────── */
.lt-empty {
  text-align: center;
  background: var(--surface-container);
  border-radius: 2rem; padding: 32px 20px; margin: 10px 0;
}
.lt-empty .big { font-size: 46px; }
.lt-empty h3   { margin: 8px 0 4px !important; font-size: 22px !important; }
.lt-empty p    { color: var(--on-surface-variant); font-size: 14px; margin: 0; }

/* ── Tip, micro, note, soon-card ───────────────────────────────────────── */
.lt-tip {
  display: flex; gap: 12px; align-items: center;
  background: var(--surface-container-low);
  border-radius: 2rem; padding: 14px 16px; margin: 14px 0 8px;
}
.lt-tip .e { font-size: 30px; }
.lt-tip b  { font-family: 'Quicksand', sans-serif; font-size: 18px; display: block; }

.lt-micro {
  text-align: center;
  background: var(--surface-container-high);
  border-radius: 999px; padding: 10px 16px;
  font-size: 13px; font-weight: 500;
  color: var(--on-surface-variant); margin: 14px 0 4px;
}
.lt-note {
  display: flex; gap: 10px;
  background: var(--surface-container);
  border-radius: 1.5rem; padding: 12px 14px;
  font-size: 13px; color: var(--on-surface-variant); margin-top: 14px;
}
.lt-soon-card {
  display: flex; align-items: center; gap: 12px;
  background: var(--secondary-fixed);
  opacity: .75;
  border-radius: 1.5rem; padding: 12px 14px; margin: 4px 0 8px;
}
.lt-soon-card .t { font-weight: 600; font-size: 16px; color: var(--on-secondary-fixed); }
.lt-soon-card .d { font-size: 13px; color: var(--on-secondary-fixed-variant); }
.lt-chipnote {
  font-size: 11px; font-weight: 700; padding: 2px 8px;
  border-radius: 6px;
  background: var(--secondary-container);
  color: var(--on-secondary-container);
}

/* ── Streamlit widget overrides ────────────────────────────────────────── */
.stButton > button, .stDownloadButton > button {
  border-radius: 999px !important;
  font-weight: 700; font-size: 13px;
  border: none !important;
  background: var(--surface-container-high) !important;
  color: var(--on-surface) !important;
  padding: .35rem 1rem; min-height: 38px;
  transition: transform .1s, background .15s;
}
.stButton > button:hover {
  background: var(--surface-container-highest) !important;
  color: var(--on-surface) !important;
}
.stButton > button:active { transform: scale(.96) !important; }
.stButton > button[kind="primary"] {
  background: var(--primary-container) !important;
  color: var(--on-primary-container) !important;
  box-shadow: 0 2px 6px rgba(32,26,25,.18) !important;
}
.stButton > button[kind="primary"]:hover {
  background: var(--primary) !important; color: #fff !important;
}

.stTextInput input, .stTextArea textarea,
.stDateInput input, .stNumberInput input {
  background: var(--surface-container-lowest) !important;
  border-radius: 999px !important;
  border: 1px solid transparent !important;
  box-shadow: 0 1px 3px rgba(32,26,25,.07) !important;
}
.stTextArea textarea { border-radius: 1rem !important; }
.stTextInput > div > div, .stDateInput > div > div,
.stNumberInput > div > div, .stSelectbox > div > div {
  border-radius: 999px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
  box-shadow: 0 0 0 2px rgba(99,82,163,.35) !important;
}
[data-testid="stWidgetLabel"] p { font-weight: 600; font-size: 15px; color: var(--on-surface); }
[data-testid="stPills"] button,
[data-testid="stSegmentedControl"] button { border-radius: 999px !important; }
div[data-testid="stAlert"] { border-radius: 1rem !important; }
[data-testid="stDialog"] > div, div[role="dialog"] { border-radius: 2rem !important; }

/* ── Fixed bottom navigation ───────────────────────────────────────────── */
.st-key-nav {
  position: fixed; bottom: 0; left: 0; right: 0; z-index: 999;
  background: rgba(255,248,246,.90);
  backdrop-filter: blur(16px);
  box-shadow: 0 -2px 12px rgba(32,26,25,.06);
  padding: 6px 10px calc(8px + env(safe-area-inset-bottom,0px));
}
.st-key-nav > div { max-width: 560px; margin: 0 auto; }
.st-key-nav [data-testid="stHorizontalBlock"] {
  flex-wrap: nowrap !important; gap: 4px !important; align-items: center;
}
.st-key-nav [data-testid="stColumn"] {
  min-width: 0 !important; flex: 1 1 0 !important; width: auto !important;
}
.st-key-nav .stButton > button {
  background: transparent !important; box-shadow: none !important;
  font-size: 11px; padding: .2rem .1rem;
  min-height: 52px; border-radius: 1.25rem !important;
  color: var(--on-surface-variant) !important;
  flex-direction: column; gap: 0; width: 100%;
}
.st-key-nav .stButton > button p { font-size: 11px; font-weight: 700; margin: 0; }
.st-key-nav .stButton > button[kind="primary"] {
  background: rgba(140,159,50,.16) !important;
  color: var(--primary) !important; box-shadow: none !important;
}
.st-key-nav .st-key-nav_add button {
  background: var(--primary-container) !important;
  color: var(--on-primary-container) !important;
  width: 52px; height: 52px; min-height: 52px;
  border-radius: 50% !important;
  box-shadow: 2px 3px 0 var(--on-surface) !important;
  margin: 0 auto; display: flex;
}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
