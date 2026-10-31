from __future__ import annotations

from pathlib import Path

from playwright.sync_api import Download, Locator, Page

from framework.components.base_component import BaseComponent


class DataMenu(BaseComponent):
    """Header "Дані" dropdown: export GeoJSON/CSV, import file, load demo sample."""

    def __init__(self, page: Page) -> None:
        super().__init__(page.locator("header").filter(has=page.get_by_role("button", name="Дані")))

    @property
    def toggle(self) -> Locator:
        return self.root.get_by_role("button", name="Дані", exact=True)

    @property
    def export_geojson_item(self) -> Locator:
        return self.root.get_by_role("button", name="GeoJSON (.geojson)")

    @property
    def export_csv_item(self) -> Locator:
        return self.root.get_by_role("button", name="Таблиця Excel (.csv)")

    @property
    def import_item(self) -> Locator:
        return self.root.get_by_role("button", name="Імпортувати GeoJSON / CSV")

    @property
    def demo_item(self) -> Locator:
        return self.root.get_by_role("button", name="Завантажити демо-зразок")

    @property
    def export_caption(self) -> Locator:
        return self.root.get_by_text("Експорт даних (")

    @property
    def file_input(self) -> Locator:
        return self.root.locator("input[type='file']")

    def open(self) -> None:
        if not self.export_geojson_item.is_visible():
            self.toggle.click()
        self.export_geojson_item.wait_for(state="visible")

    def _download(self, item: Locator, target_dir: Path) -> Path:
        self.open()
        with self.page.expect_download() as info:
            item.click()
        download: Download = info.value
        path = target_dir / download.suggested_filename
        download.save_as(path)
        return path

    def export_geojson(self, target_dir: Path) -> Path:
        return self._download(self.export_geojson_item, target_dir)

    def export_csv(self, target_dir: Path) -> Path:
        return self._download(self.export_csv_item, target_dir)

    def import_file(self, path: Path) -> None:
        """Upload through the menu item, the same way a user does (file chooser)."""
        self.open()
        with self.page.expect_file_chooser() as info:
            self.import_item.click()
        info.value.set_files(path)

    def load_demo(self) -> None:
        self.open()
        self.demo_item.click()
