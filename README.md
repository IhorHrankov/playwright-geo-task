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
| [docs/test-guidelines.md](docs/test-guidelines.md) | Правила написання автотестів (з джерелами) |

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
> Без них UI- і API-тести пропускаються (`SKIPPED`).

## Запуск

```bash
pytest                                   # усе: api + ui
pytest -m smoke                          # критичний шлях (12 тестів)
pytest -m api                            # лише HTTP-перевірки, без браузера
pytest -m ui                             # лише UI

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
│   ├── storage.py                # seed localStorage; PointRecords/StoredPoints — доменні перевірки стану
│   ├── files.py                  # читання завантажених і еталонних файлів
│   ├── api/app_client.py         # HTTP-клієнти: хост Amplify, тайли CARTO/Esri
│   ├── data/
│   │   ├── fields.py             # FIELD_1…FIELD_4: полігони, площі
│   │   ├── test_data.py          # літеральні точки, очікувані списки, шляхи до файлів
│   │   ├── messages.py           # тексти інтерфейсу (toast, помилки)
│   │   └── models.py             # pydantic-моделі точки та GeoJSON-контракту
│   ├── utils/geo.py              # незалежний розрахунок: WGS84→MGRS, point-in-polygon, площа
│   ├── pages/                    # Page Objects (BasePage → StartPage, FieldsGisPage)
│   └── components/               # FieldsList, PointsPanel, PointCard, DataMenu, AddPointModal, MapView, Toast
├── tests/
│   ├── conftest.py               # Basic Auth для контекстів, локаль uk-UA, TZ Europe/Kyiv
│   ├── known_bugs.py             # реєстр дефектів → strict xfail
│   ├── ui/                       # e2e: поля, додавання, список, експорт, імпорт, карта, старт
│   └── api/                      # auth, статика, контракт demo-GeoJSON, тайли, security headers
├── test_data/
│   ├── import/                   # файли для імпорту (валідні, пошкоджені, з невалідними даними)
│   ├── expected/                 # еталонні результати експорту
│   └── state/                    # стан localStorage до тестування, геометрія полів
├── scripts/check_test_style.py   # перевірка «без логіки в тестах» (запускається в CI)
├── docs/                         # чек-лист, тест-кейси, баг-репорти, тестові дані, правила, підхід
└── .github/workflows/tests.yml   # CI: lint + style → api + ui, артефакти звітів
```

## Практики, закладені у фреймворк

Детально, з прикладами і джерелами, — у [docs/test-guidelines.md](docs/test-guidelines.md). Коротко:

* **Тест — тільки сценарій і перевірки.** Без циклів, `if`, comprehension, арифметики, f-рядків
  (гарантує `python scripts/check_test_style.py`); варіанти — через `parametrize` з `ids`.
* **Очікування записані наперед**: літеральні дані в `framework/data/test_data.py`, еталонні
  файли в `test_data/expected/`, тексти UI в `messages.py`.
* **DAMP > DRY**, Arrange / Act / Assert, одна поведінка на тест, назва = очікувана поведінка.
* **Page Object + компоненти**: локатори-властивості, дії-дієслова, доменні запити;
  `assert` / `expect` — тільки в тестах.
* **Web-first assertions** і локатори за роллю/підписом; очікування анімацій Leaflet — у `MapView`.
* **Ізоляція**: свій browser context і засіяний localStorage на кожен тест → паралельний запуск.
* **Відомі дефекти** — strict `xfail` з ID бага; секрети — лише в `.env` / секретах CI.

## Обмеження

* Автотести написані й перевірені статично (імпорт модулів, збирання тестів, перевірка стилю).
  Селектори звірено з DOM живого застосунку. Повний прогін UI/API потрібно виконати на машині
  з доступом до сайту; середовище, де готувався репозиторій, не мало мережевого доступу до нього.
* Мобільна верстка, Firefox/WebKit і відкриття CSV в Excel вручну не перевірялися (див.
  [docs/approach.md](docs/approach.md)).
