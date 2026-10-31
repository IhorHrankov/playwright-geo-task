"""Control of the app's client-side state (monitoring points live in localStorage)."""

from __future__ import annotations

import json
from collections.abc import Iterable

from playwright.sync_api import BrowserContext, Page

from framework.data.models import STORAGE_KEY, MonitoringPoint

# Seeds localStorage once per tab: sessionStorage survives reloads, so a reload keeps
# whatever the app saved instead of re-seeding (needed for persistence checks).
_SEED_SCRIPT = """
(([key, value]) => {
  if (!window.sessionStorage.getItem('__qa_seeded')) {
    window.localStorage.setItem(key, value);
    window.sessionStorage.setItem('__qa_seeded', '1');
  }
})(%s);
"""


def seed_points(context: BrowserContext, points: Iterable[MonitoringPoint]) -> None:
    """Must be called before the first navigation of the page under test."""
    payload = json.dumps([p.to_storage() for p in points], ensure_ascii=False)
    context.add_init_script(_SEED_SCRIPT % json.dumps([STORAGE_KEY, payload], ensure_ascii=False))


def read_points(page: Page) -> list[dict]:
    raw = page.evaluate("key => window.localStorage.getItem(key)", STORAGE_KEY)
    return json.loads(raw) if raw else []
