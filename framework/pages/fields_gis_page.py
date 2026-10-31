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

    def open_add_point_modal(self, field: Field, u: float = 0.5, v: float = 0.5) -> tuple[float, float]:
        """Make ``field`` active, click inside it and return the clicked (lat, lng)."""
        if not self.fields.card(field).is_active():
            self.select_field(field)
        lat_lng = self.map.click_inside(field, u, v)
        self.add_point_modal.root.wait_for(state="visible")
        return lat_lng
