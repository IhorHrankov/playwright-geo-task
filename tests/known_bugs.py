"""Single registry of documented defects (docs/bug-reports.md).

A test that reproduces a defect asserts the *expected* behaviour and is wrapped in
``known_bug(...)``: it is reported as XFAIL while the bug exists and turns into a hard
failure (strict xfail) as soon as the bug is fixed, so the marker gets removed on purpose.
"""

from __future__ import annotations

import pytest

BUGS: dict[str, str] = {
    "BUG-01": "Import accepts points outside every field and binds them to a field",
    "BUG-02": "Import accepts out-of-range coordinates (lat 95, lng 200)",
    "BUG-03": "Duplicate IDs inside an imported file break the list and delete together",
    "BUG-04": "Import accepts invalid createdAt; sorting becomes unpredictable",
    "BUG-05": "Imported MGRS is trusted without recalculation",
    "BUG-06": "Re-import / demo sample duplicates existing points",
    "BUG-07": "Streets basemap (CARTO) returns 'API KEY REQUIRED' placeholder tiles",
    "BUG-08": "Field area differs from polygon geometry by 2.5-3.5x",
    "BUG-09": "CSV export is vulnerable to formula injection",
    "BUG-10": "Repeated 'Показати на карті' for the same point does not re-center",
    "BUG-11": "Search/type filter is not applied to map markers",
    "BUG-12": "Export silently exports only the filtered subset",
    "BUG-13": "Wrong plural form in import toast ('1 точок')",
    "BUG-14": "Point is deleted without confirmation or undo",
    "BUG-15": "Duplicate id='task-result' on the start page",
    "BUG-16": "Security headers are missing (HSTS, nosniff, X-Frame-Options, CSP)",
}


def known_bug(bug_id: str) -> pytest.MarkDecorator:
    return pytest.mark.xfail(reason=f"{bug_id}: {BUGS[bug_id]}", strict=True)
