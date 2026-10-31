# CLAUDE.md

QA-репозиторій вебзастосунку **AgTech Fields GIS**: UI-автотести (Python + Playwright + pytest)
і ручні артефакти в `docs/`. Коду застосунку тут немає, тести йдуть проти живого сайту на AWS Amplify.
У застосунку немає бекенду: усі дані точок живуть у `localStorage`.

Усі описи, інструкції, дефекти, docstring'и й коментарі пишемо **українською**. Назви в коді
(функції, тести, змінні) — англійською.

## Команди

```bash
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements.txt ruff pycodestyle
.venv/bin/playwright install chromium

.venv/bin/pytest -n 4 --browser chromium            # усі тести, 1–3 хв
.venv/bin/pytest -m smoke --browser chromium        # критичний шлях
.venv/bin/pytest tests/ui/test_import.py -k demo    # окремі тести
.venv/bin/pytest --runxfail -k <назва>              # реальна причина падіння під known_bug

.venv/bin/pytest --headed --slowmo 500 -k <назва>   # подивитися тест у браузері

scripts/lint.sh                                     # ruff, ruff format, pycodestyle, стиль тестів (як у CI)
.venv/bin/ruff check --fix . && .venv/bin/ruff format .   # автовиправлення
```

Потрібен `.env` з `APP_USERNAME` / `APP_PASSWORD` (зразок — `.env.example`). Без нього всі тести
`SKIPPED`, і це не успішний прогін. Не виводьте вміст `.env` і не комітьте його.

## Архітектура

```
tests/ui/test_*.py → сценарій і перевірки
tests/ui/conftest.py → open_gis_with([...]), gis_page (5 точок), empty_gis_page (0 точок)
tests/known_bugs.py → реєстр BUG-xx → strict xfail
framework/pages, components → локатори, дії, доменні запити (без assert/expect)
framework/storage.py → засівання localStorage, StoredPoints — перевірки стану
framework/data → тексти (ui_texts.json), літеральні дані (test_data.py), поля (fields.py)
framework/utils/geo.py → незалежний оракул: MGRS, point-in-polygon, площа
test_data/ → файли імпорту та еталони експорту (expected/)
```

Правила написання тестів — у [docs/test-guidelines.md](docs/test-guidelines.md). Ними керуються
скіли `/write-test` (написання) і `/review-tests` (ревʼю).

## Що неочевидно

- **XFAIL — це норма.** Очікуваний результат зараз: усе `passed` або `xfailed`. Strict xfail: якщо
  баг виправлено, тест падає як `XPASS(strict)` — приберіть маркер і закрийте репорт.
- **Перевіряйте причину xfail.** `xfail` приховує будь-яке падіння, зокрема зламаний локатор.
  Новий чи змінений `known_bug`-тест прогоняйте з `--runxfail`.
- **Перевірка стану «нічого не змінилось» може пройти до завершення дії.** Демо-зразок і імпорт
  асинхронні, і лічильник оновлюється ~за 100 мс після кліку. Спершу дочекайтеся сигналу
  завершення (toast), потім перевіряйте: приклад — `test_loading_demo_twice_does_not_duplicate_points`.
- **Стан задається до навігації.** `seed_points` викликається до першого `goto`; засівання одноразове
  на вкладку, тож `reload` не стирає збережене застосунком.
- **Карта.** Leaflet не дає геокоординат у DOM, кліки обчислюються в `MapView`; перед кліком чекайте
  завершення анімації (`wait_until_idle`). Фіксованих пауз у тестах немає.
- **Порядок у файлах імпорту різний:** `valid_points.csv` — `std-4…std-1`, `valid_points.geojson` —
  `std-1…std-4`; localStorage зберігає порядок файлу.

- **Тексти — у `framework/data/ui_texts.json`** (сторінка → компонент → ключ): у тесті
  `UI.fields_gis.points.heading(count=6)`, усередині JSON посилання `{@шлях.до.ключа}`.
- **Мережа нестабільна.** Навігація не чекає подію `load`, готовність визначає `ready_marker`; тайли
  сторонніх сервісів мають окремий таймаут. Перед висновком про дефект повторіть падіння.

## Обсяг

Стартова сторінка (`#/`) і HTTP-рівень свідомо не тестуються автоматично: не додавайте такі тести
без запиту. BUG-16 (security-заголовки) — ручна перевірка, у `known_bugs.py` його немає.

## Зміна разом із тестами

Новий, перейменований або видалений тест чи дефект оновлює також:
`docs/checklist.md`, `docs/test-cases.md`, `docs/bug-reports.md`, `tests/known_bugs.py`,
лічильники в `README.md` (кількість багів, smoke-тестів, результат останнього прогону).
