# AgTech Fields GIS — QA

Результати тестування веб-застосунку **AgTech Fields GIS**
(<https://main.d8gkeeaiko6qy.amplifyapp.com/#/test>): чек-лист, тест-кейси, баг-репорти,
тестові дані та автотести на **Python + Playwright** (UI і HTTP/API).

| Документ | Що всередині |
| --- | --- |
| [docs/approach.md](docs/approach.md) | Підхід, обсяг, ризики, що не перевірялося |
| [docs/checklist.md](docs/checklist.md) | Чек-лист на 36 перевірок із результатами |
| [docs/test-cases.md](docs/test-cases.md) | Тест-кейси для ключових сценаріїв + зв'язок з автотестами |
| [docs/bug-reports.md](docs/bug-reports.md) | 16 баг-репортів (1 Critical, 5 Major, 7 Minor, 3 Trivial) |
| [docs/test-data.md](docs/test-data.md) | Усі тестові дані, що використовувалися, і де вони лежать |

## Швидкий старт

Потрібно: Python 3.11+, доступ до інтернету (сайт на AWS Amplify, тайли CARTO / Esri).

```bash
git clone <repo-url> agtech-fields-qa && cd agtech-fields-qa
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium          # браузер для UI-тестів

cp .env.example .env                 # впишіть APP_USERNAME / APP_PASSWORD (Basic Auth)
```

> Облікові дані читаються тільки зі змінних оточення або `.env` (він у `.gitignore`).
> Без них UI- і API-тести пропускаються (`SKIPPED`), unit-тести працюють завжди.

## Запуск

```bash
pytest                                   # усе: unit + api + ui
pytest -m smoke                          # критичний шлях (~13 тестів)
pytest -m api                            # лише HTTP-перевірки, без браузера
pytest -m ui                             # лише UI
pytest -m unit -o addopts=""             # офлайн-перевірки фреймворку (без Playwright-плагіна)

pytest -m ui --headed --slowmo 300       # подивитися, що робить браузер
pytest -m ui --browser firefox --browser webkit
pytest -n auto                           # паралельно (pytest-xdist); тести незалежні
pytest -m ui -k import                   # лише тести імпорту
pytest -m ui --runxfail                  # показати реальні падіння на відомих дефектах
pytest --base-url https://<інше-оточення>   # або BASE_URL у .env

pytest --html=test-results/report.html --self-contained-html   # HTML-звіт
```

Після падіння UI-тесту в `test-results/artifacts/` зберігаються **trace**, скріншот і відео
(`--tracing=retain-on-failure` у `pyproject.toml`). Відкрити trace:
`playwright show-trace test-results/artifacts/<test>/trace.zip`.

### Як читати результат

Тести на задокументовані дефекти перевіряють **очікувану** поведінку й позначені
`known_bug("BUG-xx")` (strict `xfail`):

* `XFAIL` — баг ще є, звіт зелений;
* `XPASS(strict)` → **FAILED** — баг виправлено, приберіть маркер і закрийте репорт.

Реєстр маркерів — [`tests/known_bugs.py`](tests/known_bugs.py), він збігається з
[docs/bug-reports.md](docs/bug-reports.md).

## Структура

```
.
├── framework/                    # спільний код фреймворку, без тестів
│   ├── config.py                 # Settings з env/.env (BASE_URL, APP_USERNAME, APP_PASSWORD)
│   ├── storage.py                # seed/read localStorage (стан застосунку)
│   ├── api/app_client.py         # HTTP-клієнти: хост Amplify, тайли CARTO/Esri
│   ├── data/
│   │   ├── fields.py             # еталонні поля (полігони, площі)
│   │   ├── models.py             # pydantic-моделі точки та GeoJSON-контракту
│   │   ├── builders.py           # make_point(), генерація CSV/GeoJSON у форматі застосунку
│   │   └── datasets.py           # іменовані набори даних для seed
│   ├── utils/geo.py              # незалежний оракул: WGS84→MGRS, point-in-polygon, площа
│   ├── pages/                    # Page Objects (BasePage → StartPage, FieldsGisPage)
│   └── components/               # компоненти сторінки: FieldsList, PointsPanel, PointCard,
│                                 #   DataMenu, AddPointModal, MapView, Toast
├── tests/
│   ├── conftest.py               # Basic Auth для контекстів, локаль uk-UA, TZ Europe/Kyiv
│   ├── known_bugs.py             # реєстр дефектів → strict xfail
│   ├── ui/                       # e2e: поля, додавання, список, експорт, імпорт, карта, старт
│   ├── api/                      # auth, статика, контракт demo-GeoJSON, тайли, security headers
│   └── unit/                     # перевірки оракула та білдерів (офлайн)
├── test_data/                    # файли, використані під час ручного тестування та в автотестах
├── docs/                         # чек-лист, тест-кейси, баг-репорти, тестові дані, підхід
└── .github/workflows/tests.yml   # CI: lint + unit → api + ui, артефакти звітів
```

## Практики, закладені у фреймворк

* **Page Object + компоненти** (за мотивами
  [гайду anton.qa](https://www.anton.qa/blog/posts/page-object-model-in-playwright-with-typescript-complete-guide#best-practices)):
  `BasePage` з абстрактними `path` і `ready_marker`; кожен компонент обмежений своїм `root`
  (`section[aria-labelledby=…]`, `role=dialog`, `role=main`); локатори — властивості
  (резолвляться ліниво); дії — короткі методи-дієслова (`select_field`, `open_add_point_modal`,
  `export_csv`); **асерти лише в тестах**.
* **Локатори з пріоритетом доступності**: `get_by_role` / `get_by_label` з українськими
  назвами з UI; CSS лише для Leaflet (у нього немає ролей).
* **Фікстури замість ручного створення об'єктів**: `gis_page`, `empty_gis_page`, `open_gis(points)`,
  `start_page`, `app`, `tiles`, `anonymous_request`.
* **Детермінований стан**: localStorage засівається `add_init_script` до першого завантаження;
  перезавантаження не перезаписує дані (перевірка збереження чесна). Кожен тест має власний
  browser context → тести незалежні й паралеляться.
* **Незалежний тестовий оракул**: MGRS, належність точки полю й площа рахуються власним кодом
  (`framework/utils/geo.py`, покрито unit-тестами на еталонних значеннях), а не беруться
  із застосунку.
* **Web-first assertions** (`expect(...)`) без `sleep`; очікування завершення анімацій Leaflet
  інкапсульовано в `MapView.wait_until_idle()`.
* **Секрети поза кодом**, `xfail_strict`, `--strict-markers`, trace/скріншот/відео на падіння,
  ретраї лише в CI (`--reruns 1`), ruff-лінт.

## Обмеження

* Автотести написані й перевірені статично (імпорт, збирання 140 тестів, unit-тести — зелені).
  Селектори звірено з DOM живого застосунку. Повний прогін UI/API потрібно виконати на машині
  з доступом до сайту; середовище, де готувався репозиторій, не мало мережевого доступу до нього.
* Мобільна верстка, Firefox/WebKit і відкриття CSV в Excel вручну не перевірялися (див.
  [docs/approach.md](docs/approach.md)).
