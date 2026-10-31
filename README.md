# AgTech Fields GIS — QA

Результати тестування веб-застосунку **AgTech Fields GIS**
(<https://main.d8gkeeaiko6qy.amplifyapp.com/#/test>): чек-лист, тест-кейси, баг-репорти,
тестові дані та UI-автотести на **Python + Playwright**.

| Документ | Що всередині |
| --- | --- |
| [docs/approach.md](docs/approach.md) | Підхід, ризики, класифікація дефектів |
| [docs/checklist.md](docs/checklist.md) | Чек-лист на 36 перевірок із результатами |
| [docs/test-cases.md](docs/test-cases.md) | Тест-кейси для ключових сценаріїв + зв'язок з автотестами |
| [docs/bug-reports.md](docs/bug-reports.md) | 15 баг-репортів (1 Critical, 5 Major, 7 Minor, 2 Trivial) |
| [docs/test-data.md](docs/test-data.md) | Усі тестові дані, що використовувалися, і де вони лежать |
| [docs/test-guidelines.md](docs/test-guidelines.md) | Правила написання автотестів |

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
> Без них тести пропускаються (`SKIPPED`).

## Запуск

```bash
pytest                                   # усі тести
pytest -m smoke                          # критичний шлях (8 тестів)

pytest --headed --slowmo 500             # подивитися, що робить браузер
pytest --browser firefox --browser webkit
pytest -n auto                           # паралельно (pytest-xdist); тести незалежні
pytest -k import                         # лише тести імпорту
pytest --runxfail                        # показати реальні падіння на відомих дефектах
pytest --base-url https://<інше-оточення>   # або BASE_URL у .env

pytest --html=test-results/report.html --self-contained-html   # HTML-звіт
```

Після падіння тесту в `test-results/artifacts/` зберігаються **trace**, скріншот і відео
(`--tracing=retain-on-failure` у `pyproject.toml`). Відкрити trace:
`playwright show-trace test-results/artifacts/<test>/trace.zip`.

### Лінтер і стиль коду

```bash
pip install ruff pycodestyle
scripts/lint.sh                          # усі перевірки нижче, те саме запускає CI
ruff check --fix . && ruff format .      # автовиправлення
```

| Перевірка | Команда | Що контролює |
| --- | --- | --- |
| Лінтер | `ruff check .` | помилки коду (pyflakes), імена за PEP 8 (pep8-naming), bugbear, імпорти, стиль pytest |
| Форматування | `ruff format --check .` | єдине форматування: пробіли, порожні рядки, переноси |
| PEP 8 | `pycodestyle --config=.pycodestyle .` | стиль коду за PEP 8; довжина рядка до 110 символів |
| Стиль тестів | `python scripts/check_test_style.py` | відсутність логіки в тілі `test_*` |

Налаштування: `[tool.ruff]` у `pyproject.toml` і `.pycodestyle`. Помилка будь-якої перевірки зупиняє CI
до запуску тестів.

### Як читати результат

Тести на задокументовані дефекти перевіряють **очікувану** поведінку й позначені
`known_bug("BUG-xx")` (strict `xfail`):

* `XFAIL` — баг ще є, звіт зелений;
* `XPASS(strict)` → **FAILED** — баг виправлено, приберіть маркер і закрийте репорт.

Реєстр маркерів — [`tests/known_bugs.py`](tests/known_bugs.py). Він збігається з
[docs/bug-reports.md](docs/bug-reports.md), окрім BUG-16 (перевірено лише вручну, автотесту немає).

## Структура

```
.
├── framework/                    # спільний код фреймворку, без тестів
│   ├── config.py                 # Settings з env/.env (BASE_URL, APP_USERNAME, APP_PASSWORD)
│   ├── storage.py                # seed localStorage; PointRecords/StoredPoints — доменні перевірки стану
│   ├── files.py                  # читання завантажених і еталонних файлів
│   ├── data/
│   │   ├── fields.py             # FIELD_1…FIELD_4: полігони, площі
│   │   ├── test_data.py          # літеральні точки, очікувані списки, шляхи до файлів
│   │   ├── ui_texts.json         # тексти: сторінка → компонент → ключ, посилання {@шлях}
│   │   ├── ui_texts.py           # доступ до текстів: UI.fields_gis.points.heading(count=6)
│   │   └── models.py             # pydantic-модель точки, типи точок
│   ├── utils/geo.py              # незалежний розрахунок: WGS84→MGRS, point-in-polygon, площа
│   ├── pages/                    # Page Objects (BasePage → FieldsGisPage)
│   └── components/               # FieldsList, PointsPanel, PointCard, DataMenu, AddPointModal, MapView, Toast
├── tests/
│   ├── conftest.py               # Basic Auth для контекстів, локаль uk-UA, TZ Europe/Kyiv
│   ├── known_bugs.py             # реєстр дефектів → strict xfail
│   └── ui/                       # e2e: поля, додавання, список, експорт, імпорт, карта
├── test_data/
│   ├── import/                   # файли для імпорту (валідні, пошкоджені, з невалідними даними)
│   ├── expected/                 # еталонні результати експорту
│   └── state/                    # стан localStorage до тестування, геометрія полів
├── scripts/lint.sh               # усі статичні перевірки: ruff, pycodestyle, стиль тестів
├── scripts/check_test_style.py   # перевірка «без логіки в тестах»
├── docs/                         # чек-лист, тест-кейси, баг-репорти, тестові дані, правила, підхід
├── .claude/skills/               # інструкції для Claude Code: write-test, review-tests
├── CLAUDE.md                     # орієнтир у проєкті для Claude Code
└── .github/workflows/tests.yml   # CI: scripts/lint.sh → ui, артефакти звітів
```

## Практики, закладені у фреймворк

Детально, з прикладами, — у [docs/test-guidelines.md](docs/test-guidelines.md). Коротко:

* **Тест — тільки сценарій і перевірки.** Без циклів, `if`, comprehension, арифметики, f-рядків
  (гарантує `python scripts/check_test_style.py`); варіанти — через `parametrize` з `ids`.
* **Очікування записані наперед**: літеральні дані в `framework/data/test_data.py`, еталонні
  файли в `test_data/expected/`, тексти в `framework/data/ui_texts.json`.
* **DAMP > DRY**, Arrange / Act / Assert, одна поведінка на тест, назва = очікувана поведінка.
* **Page Object + компоненти**: локатори-властивості, дії-дієслова, доменні запити;
  `assert` / `expect` — тільки в тестах.
* **Web-first assertions** і локатори за роллю/підписом; очікування анімацій Leaflet — у `MapView`.
* **Ізоляція**: свій browser context і засіяний localStorage на кожен тест → паралельний запуск.
* **Відомі дефекти** — strict `xfail` з ID бага; секрети — лише в `.env` / секретах CI.

## Обмеження

* Останній повний прогін на живому застосунку (31.10.2026, Chromium): **78 passed, 21 xfailed**.
  Firefox і WebKit не запускалися.
* Стартова сторінка (`#/`) і HTTP-рівень (Basic Auth, статика, контракт demo-GeoJSON) автотестами
  не покриті; security-заголовки (BUG-16) перевірено лише вручну.
* Мобільна верстка, Firefox/WebKit і відкриття CSV в Excel вручну не перевірялися.
