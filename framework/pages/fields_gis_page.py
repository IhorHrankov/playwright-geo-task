"""Main application page (#/test): sidebar with fields and points, map, header data menu."""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from framework.components import AddPointModal, DataMenu, FieldsList, MapView, PointsPanel, Toast
from framework.data.fields import Field
from framework.pages.base_page import BasePage


class FieldsGisPage(BasePage):
    path = "/#/test"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.data_menu = DataMenu(page)
        self.fields = FieldsList(page)
        self.points = PointsPanel(page)
        self.map = MapView(page)
        self.add_point_modal = AddPointModal(page)
        self.toast = Toast(page)

    @property
    def ready_marker(self) -> Locator:
        return self.map.field_polygons.first

    @property
    def app_title(self) -> Locator:
        return self.page.get_by_role("heading", level=1, name="AgTech Fields GIS")

    def wait_until_ready(self) -> None:
        super().wait_until_ready()
        self.map.wait_until_idle()

    # --- workflows used by several specs ---
    def select_field(self, field: Field) -> None:
        self.fields.card(field).select()
        self.map.wait_until_idle()

    def open_add_point_modal(self, field: Field) -> None:
        """Make ``field`` active and click in its centre."""
        if self.fields.card(field).root.get_attribute("aria-pressed") != "true":
            self.select_field(field)
        self.map.click_inside(field)
        self.add_point_modal.root.wait_for(state="visible")

    def add_point(self, field: Field, point_type, description: str = "") -> None:
        self.open_add_point_modal(field)
        self.add_point_modal.add(point_type, description)
