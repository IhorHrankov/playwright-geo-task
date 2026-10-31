---
name: write-test
description: Написання або зміна UI-автотестів цього проєкту (pytest + Playwright, page objects, known_bug). Використовуй, коли просять додати чи полагодити тест, автоматизувати тест-кейс або відтворити дефект автотестом.
---

# Написання автотесту

Повні правила з обґрунтуванням — у `docs/test-guidelines.md`. Прочитай його перед першим тестом у сесії.

## Порядок роботи

1. **Перевір реальну поведінку.** Не вгадуй локатори й тексти: подивись DOM живого застосунку через
   короткий скрипт Playwright або запусти наявний тест. Якщо поведінка неочевидна, зафіксуй її
   спостереженням, а не припущенням.
2. **Знайди місце.** Тест іде в наявний `tests/ui/test_<область>.py`. Спершу пошукай наявні методи
   в `framework/pages` і `framework/components`, фікстури в `tests/ui/conftest.py`, дані в
   `framework/data/test_data.py`, тексти в `framework/data/ui_texts.json`.
3. **Напиши тест,** потім за потреби додай локатор чи дію в компонент.
4. **Запусти й перевір** (див. «Готовність»).

## Форма тесту

```python
def test_deleting_point_removes_it_from_storage(gis_page: FieldsGisPage) -> None:
    gis_page.points.card(SOIL_SAMPLE_FIELD_1.description).delete()
    expect(gis_page.points.heading).to_have_text(UI.fields_gis.points.heading(count=4))

    assert StoredPoints(gis_page.page).ids() == ["std-2", "std-3", "std-4", "std-5"]
```

- **Назва** — очікувана поведінка: `test_<що відбувається>_<за яких умов>`.
- **Один тест — одна поведінка,** блоки Arrange / Act / Assert розділені порожнім рядком.
- **Без логіки в тілі тесту:** цикли, `if`, comprehension, `lambda`, арифметика, f-рядки, індексація,
  `try/except` заборонені. Варіанти — через `@pytest.mark.parametrize` з читабельними `ids`.
- **Очікування записані наперед:** тексти з `ui_texts.json`, літерали, еталонні файли
  (`test_data/expected/`). Не обчислюй їх у тесті.
- **Тексти не вписуй у тест:** додай ключ у `ui_texts.json` (сторінка → компонент → ключ) і звертайся
  через `UI.fields_gis.<компонент>.<ключ>`; змінне значення — плейсхолдер `{count}`, повторюваний текст —
  посилання `{@шлях.до.ключа}`. Технічні значення (id, MGRS, атрибути) лишаються в тесті.
- **Модуль** починається з `pytestmark = [pytest.mark.ui, pytest.mark.regression]`; `smoke` — лише для
  критичного шляху.

## Що де живе

| Потрібно | Куди |
| --- | --- |
| Локатор, дія, доменний запит (без `assert` / `expect`) | `framework/components/*`, `framework/pages/*` |
| Перевірка стану localStorage (повертає id порушників) | `framework/storage.py` |
| Точки, очікувані списки, шляхи до файлів | `framework/data/test_data.py` |
| Текст інтерфейсу або текстові вхідні дані | `framework/data/ui_texts.json` |
| Файл для імпорту / еталон експорту | `test_data/import/`, `test_data/expected/` + опис у `docs/test-data.md` |

## Перевірки й очікування

- UI — тільки web-first `expect(locator)`; не `assert locator.is_visible()` чи `inner_text()` у тесті.
- `assert` — лише для даних поза DOM (файл, localStorage) і **після** `expect`, який дочекався дії.
- Локатори: `get_by_role` / `get_by_label` з текстом інтерфейсу; CSS — лише для Leaflet.
- Жодних `wait_for_timeout` і `sleep` у тестах.
- Сторонні сервіси (тайли) повільні: задай явний таймаут, як `TILE_LOAD_MS` у `test_map.py`.
- **Перевірка «нічого не змінилось» потребує сигналу завершення.** Значення може збігатися ще до дії:
  закрий попередній toast, виконай дію, дочекайся нового toast, потім перевіряй лічильник.
- Стан — через `gis_page`, `empty_gis_page` або `open_gis_with([...])`, тести незалежні між собою.

## Відомий дефект

Тест перевіряє **правильну** поведінку й позначений маркером:

```python
@known_bug("BUG-06")
def test_loading_demo_twice_does_not_duplicate_points(empty_gis_page: FieldsGisPage) -> None:
```

1. Додай дефект українською в `BUGS` (`tests/known_bugs.py`) і повний репорт у `docs/bug-reports.md`.
2. Підтверди причину: `--runxfail` має показати падіння саме через цей дефект, а не через локатор чи таймаут.
3. Для швидкого падіння в останній перевірці використовуй `timeout=1_000`.

## Готовність

Усе нижче має виконатися, у звіті наведи фактичний результат:

```bash
scripts/lint.sh
.venv/bin/pytest <файл або -k назва> --browser chromium
.venv/bin/pytest <файл> --browser chromium -n 4     # нестабільність: повтори кілька разів разом із сусідами
```

- Прогін без `.env` дає `SKIPPED` — це **не** підтвердження, що тест працює.
- Нова перевірка має вміти падати: тимчасово зміни очікуване значення й переконайся, що тест червоний.
- Оновлено документацію: `docs/checklist.md`, `docs/test-cases.md`, за потреби лічильники в `README.md`.
- Описи, docstring'и й коментарі — українською.
