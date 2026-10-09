"""Reusable HTML snippets. All user-supplied text is escaped."""
from __future__ import annotations

from html import escape

from .models import (
    STATUS_EXPIRED, STATUS_FRESH, STATUS_SOON, Product, category_emoji, category_label,
    describe_days, short_badge,
)

_CSS_CLASS = {STATUS_EXPIRED: "ick", STATUS_SOON: "soon", STATUS_FRESH: "fresh"}


def one_line(html: str) -> str:
    """Collapse whitespace so Markdown never treats indented HTML as a code block."""
    return " ".join(html.split())


def top_bar(subtitle: str, ick_count: int) -> str:
    pill = (
        '<span class="lt-fresh" style="background:#ffdad6;color:#93000a"><span class="lt-dot alert" style="background:#ba1a1a"></span>'
        f"{ick_count} in the Ick Zone</span>"
        if ick_count
        else '<span class="lt-fresh"><span class="lt-dot"></span>Fresh</span>'
    )
    avatar = (
        '<img alt="Profile" style="width:34px;height:34px;border-radius:50%;object-fit:cover" '
        'src="https://lh3.googleusercontent.com/aida/AEtjO1W_cmuwH4OaCSBD7tE2uCpCQKWV7mEbrsEpnxvCSI10cgARMsZYjGkPePRc6wlfAgUEHmSLkkFKKbFU4sSO6adliM7CorMkKjwLQAmV0qpvwUBoNYOLWkOmSM2LdZxZud-KYWhXWfZ6LbDPeyuG-QmKJP7Kox2fEREiz5J-_yYE9BN4Ea_05o1oK1gKT32dHNh9te5lWjZTP9HVeQAlbtEGakJ7WsWN2jfdR21V3pEiO8HVgdGk2DUkMYbTWejCG-cYvrd9nnMs"/>'
    )
    bell = (
        '<div style="position:relative;width:36px;height:36px;display:flex;align-items:center;justify-content:center;border-radius:50%;background:#f2e5e3">'
        '<span class="material-symbols-outlined" style="font-size:20px;color:#201a19">notifications</span>'
        + ('<span style="position:absolute;top:6px;right:6px;width:8px;height:8px;border-radius:50%;background:#ba1a1a"></span>' if ick_count else '')
        + '</div>'
    )
    return one_line(
        f'<div class="lt-top"><div class="lt-brand"><div class="lt-logo">{avatar}</div><div>'
        f'<div class="lt-brand-name">LowkeyToki</div><div class="lt-brand-sub">{escape(subtitle)}</div>'
        f'</div></div><div style="display:flex;align-items:center;gap:8px">{pill}{bell}</div></div>'
    )


def stat_grid(stats: dict) -> str:
    return one_line(
        f"""<div class="lt-grid">
        <div class="lt-stat"><div style="display:flex;justify-content:space-between;align-items:center"><span class="lbl">TOTAL INVENTORY</span><span class="material-symbols-outlined" style="font-size:18px;color:#464838">inventory_2</span></div><div><div class="num">{stats['total']}</div><div class="sub">items tracked</div></div></div>
        <div class="lt-stat soon"><div style="display:flex;justify-content:space-between;align-items:center"><span class="lbl">EXPIRING SOON</span><span class="material-symbols-outlined" style="font-size:18px;color:#493888">timer</span></div><div><div class="num">{stats[STATUS_SOON]}</div><div class="sub">next 72 hours</div></div></div>
        <div class="lt-stat ick"><span class="ghost">🦠</span><div style="display:flex;justify-content:space-between;align-items:center"><span class="lbl">THE ICK ZONE</span><span class="material-symbols-outlined" style="font-size:18px;color:#ffdad6">warning</span></div><div><div class="num">{stats[STATUS_EXPIRED]}</div><div class="sub">{'Needs attention! 🦠' if stats[STATUS_EXPIRED] else 'All clear'}</div></div></div>
        <div class="lt-stat fresh"><div style="display:flex;justify-content:space-between;align-items:center"><span class="lbl">FRESH &amp; SAFE</span><span class="material-symbols-outlined" style="font-size:18px;color:#566500">check_circle</span></div><div><div class="num">{stats[STATUS_FRESH]}</div><div class="sub">happy &amp; chill</div></div></div>
        </div>"""
    )


def health_pulse(stats: dict) -> str:
    total = stats["total"] or 1
    pct = {k: round(stats[k] * 100 / total) for k in (STATUS_EXPIRED, STATUS_SOON, STATUS_FRESH)}
    return one_line(
        f"""<div class="lt-card"><div style="display:flex;justify-content:space-between;align-items:center">
        <span class="lt-card-title">Shelf Health Pulse</span><span class="lt-pill">Total: {stats['total']}</span></div>
        <div class="lt-bar">
          <div style="width:{pct[STATUS_EXPIRED]}%;background:#362F2E"></div>
          <div style="width:{pct[STATUS_SOON]}%;background:#B9A7FF"></div>
          <div style="width:{pct[STATUS_FRESH]}%;background:#8C9F32"></div></div>
        <div class="lt-legend">
          <span><span class="lt-dot" style="background:#362F2E"></span> {stats[STATUS_EXPIRED]} Ick Zone</span>
          <span><span class="lt-dot" style="background:#B9A7FF"></span> {stats[STATUS_SOON]} Urgent</span>
          <span><span class="lt-dot" style="background:#8C9F32"></span> {stats[STATUS_FRESH]} Fresh</span></div></div>"""
    )


def section_head(title: str, count_text: str, kind: str) -> str:
    return one_line(
        f'<div class="lt-section-head"><h2>{escape(title)}</h2>'
        f'<span class="lt-count {kind}">{escape(count_text)}</span></div>'
    )


def product_row(p: Product, show_location: bool = True) -> str:
    days = p.days_left()
    cls = _CSS_CLASS[p.status()]
    meta_bits = [category_label(p.category)]
    if show_location and p.storage_location:
        meta_bits.append(p.storage_location)
    if p.quantity > 1:
        meta_bits.append(f"x{p.quantity}")
    demo = '<span class="lt-demo">DEMO</span>' if p.is_demo else ""
    return one_line(
        f"""<div class="lt-item {cls if cls == 'ick' else ''}"><div class="left">
        <div class="lt-avatar">{category_emoji(p.category)}</div>
        <div style="min-width:0"><div class="lt-name">{escape(p.name)}{demo}</div>
        <div class="lt-meta">{escape(' • '.join(meta_bits))}</div>
        <div class="lt-meta" style="font-weight:700">{escape(describe_days(days))} ({p.expiry_date.strftime('%d %b %Y')})</div></div></div>
        <span class="lt-badge {cls}">{escape(short_badge(days))}</span></div>"""
    )


def empty_state(emoji: str, title: str, body: str) -> str:
    return one_line(
        f'<div class="lt-empty"><div class="big">{emoji}</div><h3>{escape(title)}</h3><p>{escape(body)}</p></div>'
    )


def banner(pill: str, title: str, sub: str, orb: str = "🧪") -> str:
    return one_line(
        f'<div class="lt-banner"><div><span class="lt-pill">{escape(pill)}</span>'
        f'<div class="lt-hero-title" style="margin-top:8px">{escape(title)}</div>'
        f'<div class="lt-hero-sub" style="margin-bottom:0">{escape(sub)}</div></div><div class="lt-orb">{orb}</div></div>'
    )


def tip_card(emoji: str, title: str, body: str) -> str:
    return one_line(
        f'<div class="lt-tip"><div class="e">{emoji}</div><div><b>{escape(title)}</b>'
        f'<span style="font-size:14px;color:#464838">{escape(body)}</span></div></div>'
    )


def micro(text: str) -> str:
    return f'<div class="lt-micro">{escape(text)}</div>'


def note(text: str, icon: str = "ℹ️") -> str:
    return f'<div class="lt-note"><span>{icon}</span><span>{escape(text)}</span></div>'
