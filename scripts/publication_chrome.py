#!/usr/bin/env python3
"""Shared site-level publication chrome.

Generators call these pure functions while constructing HTML. Validators remain the
contract boundary; no function here reopens or mutates generated pages.
"""
from __future__ import annotations

import html

BASE = "/dc-public-realm"

PRIMARY_NAV = (
    ("Explore", f"{BASE}/"),
    ("Research missions", f"{BASE}/collaborate/"),
    ("About the research", f"{BASE}/methodology/"),
    ("Data", f"{BASE}/data/"),
)


def primary_nav() -> str:
    links = "".join(
        f'<a href="{html.escape(href, quote=True)}">{html.escape(label)}</a>'
        for label, href in PRIMARY_NAV
    )
    return f'<nav class="primary-nav" aria-label="Primary">{links}</nav>'


def site_state() -> str:
    return '<span class="site-state" aria-label="Site status: alpha">Alpha</span>'


def header(kicker: str = "Diplomatic Gifts in Washington · public art research") -> str:
    return (
        '<header>'
        + site_state()
        + f'<div class="kicker">{html.escape(kicker)}</div>'
        + primary_nav()
        + '</header>'
    )
