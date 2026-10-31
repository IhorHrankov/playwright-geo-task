from __future__ import annotations

from playwright.sync_api import Locator, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from framework.components.base_component import BaseComponent
from framework.data.fields import Field

BASEMAP_BUTTONS = {"streets": "Схема", "satellite": "Супутник"}


class MapView(BaseComponent):
    """Leaflet map: field polygons (SVG paths), point markers, basemap switcher, focus button.

    Leaflet does not expose geo coordinates in the DOM, so clicks at a given lat/lng are
    computed from the rendered polygon's bounding box and the field's known geometry
    (linear interpolation; Mercator distortion over ~1 km is far below one pixel).
    """

    def __init__(self, page: Page) -> None:
        super().__init__(page.get_by_role("main", name="Робоча область інтерактивної карти"))

    # --- locators ---
    @property
    def container(self) -> Locator:
        return self.root.locator(".leaflet-container")

    @property
    def field_polygons(self) -> Locator:
        return self.root.locator(".leaflet-overlay-pane path.leaflet-interactive")

    @property
    def markers(self) -> Locator:
        return self.root.locator(".leaflet-marker-pane .leaflet-marker-icon")

    @property
    def tiles(self) -> Locator:
        return self.root.locator(".leaflet-tile-pane img.leaflet-tile")

    @property
    def popup(self) -> Locator:
        return self.root.locator(".leaflet-popup")

    @property
    def hint(self) -> Locator:
        return self.root.get_by_text("Клікніть всередині активного поля, щоб додати точку")

    @property
    def focus_button(self) -> Locator:
        return self.root.get_by_role("button", name="Сфокусувати активне поле")

    def basemap_button(self, basemap: str) -> Locator:
        return self.root.get_by_role("button", name=BASEMAP_BUTTONS[basemap], exact=True)

    def polygon(self, field: Field) -> Locator:
        # react-leaflet renders the GeoJSON layers in the same order as the fields list
        return self.field_polygons.nth(field.order)

    # --- helpers ---
    def wait_until_idle(self, timeout_ms: int = 5_000) -> None:
        """Wait until pan/zoom animations finish (Leaflet adds *-anim classes while animating)."""
        self.page.wait_for_function(
            """() => {
                const m = document.querySelector('.leaflet-container');
                return m && !m.classList.contains('leaflet-zoom-anim')
                       && !document.querySelector('.leaflet-pan-anim');
            }""",
            timeout=timeout_ms,
        )
        # flyTo/fitBounds may still move the map without those classes; wait for a stable polygon box
        previous = None
        for _ in range(20):
            box = self.field_polygons.first.bounding_box()
            if box == previous:
                return
            previous = box
            self.page.wait_for_timeout(100)

    def _pixel_for(self, field: Field, lat: float, lng: float) -> tuple[float, float]:
        box = self.polygon(field).bounding_box()
        assert box, f"polygon of {field.id} is not rendered"
        min_lng, min_lat, max_lng, max_lat = field.bounds
        x = box["x"] + (lng - min_lng) / (max_lng - min_lng) * box["width"]
        y = box["y"] + (max_lat - lat) / (max_lat - min_lat) * box["height"]
        return x, y

    def tiles_from(self, host: str) -> Locator:
        return self.root.locator(f".leaflet-tile-pane img.leaflet-tile[src*='{host}']")

    def loaded_street_tiles_are_distinct(self) -> bool:
        """CARTO answers every tile with one identical 'API KEY REQUIRED' image when the key is missing."""
        sources = self.tiles_from("basemaps.cartocdn.com").evaluate_all("imgs => imgs.map(i => i.src)")
        bodies = {self.page.request.get(src).body() for src in sources[:4]}
        return len(bodies) > 1

    def polygon_position(self, field: Field) -> dict:
        return self.polygon(field).bounding_box()

    # --- actions ---
    def click_at(self, field: Field, lat: float, lng: float) -> None:
        """Click the map at a geographic point, using ``field`` as the pixel reference."""
        self.wait_until_idle()
        x, y = self._pixel_for(field, lat, lng)
        self.page.mouse.click(x, y)

    def click_inside(self, field: Field, u: float = 0.5, v: float = 0.5) -> tuple[float, float]:
        lat, lng = field.interior_point(u, v)
        self.click_at(field, lat, lng)
        return lat, lng

    def click_outside_fields(self, reference: Field) -> None:
        """Click just south-west of ``reference`` where no field polygon is drawn."""
        min_lng, min_lat, _, _ = reference.bounds
        self.click_at(reference, min_lat - 0.002, min_lng - 0.002)

    def select_basemap(self, basemap: str) -> None:
        self.basemap_button(basemap).click()

    def focus_active_field(self) -> None:
        self.focus_button.click()
        self.wait_until_idle()

    def is_a_marker_centered(self, tolerance_px: int = 25, timeout_ms: int = 3_000) -> bool:
        """True if some marker sits at the centre of the map viewport (waits for flyTo)."""
        try:
            self.page.wait_for_function(
                """tol => {
                    const map = document.querySelector('.leaflet-container').getBoundingClientRect();
                    const cx = map.left + map.width / 2, cy = map.top + map.height / 2;
                    return [...document.querySelectorAll('.leaflet-marker-icon')].some(m => {
                        const r = m.getBoundingClientRect();
                        return Math.hypot(r.left + r.width / 2 - cx, r.top + r.height / 2 - cy) <= tol;
                    });
                }""",
                arg=tolerance_px,
                timeout=timeout_ms,
            )
            return True
        except PlaywrightTimeoutError:
            return False

    def zoom_out(self, times: int = 1) -> None:
        for _ in range(times):
            self.root.locator("a.leaflet-control-zoom-out").click()
            self.wait_until_idle()

    def drag_by(self, dx: int, dy: int) -> None:
        box = self.container.bounding_box()
        assert box
        sx, sy = box["x"] + box["width"] * 0.8, box["y"] + box["height"] * 0.2
        self.page.mouse.move(sx, sy)
        self.page.mouse.down()
        self.page.mouse.move(sx + dx, sy + dy, steps=10)
        self.page.mouse.up()
        self.wait_until_idle()
