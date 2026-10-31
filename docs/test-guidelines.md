# Правила написання автотестів

Мета — тест читається як специфікація: відкрили файл, і за хвилину зрозуміло, **що** перевіряється
та **чому** впало. Правила зведені з джерел у кінці документа й закріплені в коді та CI.

## 1. Жодної логіки в тестах

У тілі `test_*` немає циклів, `if`, comprehension, `lambda`, арифметики, f-рядків, індексації
й `try/except`. Тест — це лише виклики методів page objects і перевірки.

*Чому:* логіку в тесті треба «виконати в голові», щоб зрозуміти результат. Якщо тест повторює
логіку застосунку, баг відтворюється в обох місцях і тест проходить. Складне виносимо в хелпери
й фікстури, перебір варіантів — у `@pytest.mark.parametrize`.

*Як закріплено:* `scripts/check_test_style.py` аналізує AST усіх `test_*` і валить CI при порушенні.

## 2. Очікувані значення записані наперед

Тест порівнює з літералом або з ревʼюваним еталонним файлом, а не з тим, що обчислив сам:

```python
expect(gis_page.points.heading).to_have_text("Моніторингові точки (6)")       # не f"({before + 1})"
assert read_json(exported) == read_json(EXPECTED_STANDARD_GEOJSON)            # test_data/expected/
```

Тестові дані (`framework/data/test_data.py`) — це літерали з іменами, що пояснюють суть:
`PESTS_FIELD_4`, `STANDARD_DESCRIPTIONS_NEWEST_FIRST`, `DUPLICATE_IDS_CSV`. MGRS у них записано
вручну й звірено із застосунком і незалежним конвертером.

## 3. DAMP важливіше за DRY

Тест має бути зрозумілим без стрибків по файлах (Descriptive And Meaningful Phrases). Невелике
повторення в тестах допустиме. Спільним робимо тільки те, що не важливо для розуміння тесту:
навігацію, локатори, підготовку стану. Важливе для сценарію (дані, очікуваний результат)
лишається в самому тесті.

## 4. Структура Arrange / Act / Assert і одна поведінка на тест

```python
def test_deleting_point_removes_it_from_storage(gis_page):            # Arrange — фікстура
    gis_page.points.card(SOIL_SAMPLE_FIELD_1.description).delete()      # Act
    expect(gis_page.points.heading).to_have_text("Моніторингові точки (4)")

    assert StoredPoints(gis_page.page).ids() == ["std-2", "std-3", "std-4", "std-5"]   # Assert
```

Блоки розділені порожнім рядком. Якщо тесту потрібен `if`, щоб перевірити два результати, —
це два тести (`test_description_of_250_characters_is_accepted` / `..._251_..._is_rejected`).

## 5. Назва тесту — це очікувана поведінка

`test_<що відбувається>_<за яких умов>`: `test_click_outside_active_field_shows_error_instead_of_modal`.
У параметризації — читабельні `ids` (`[by-mgrs]`, `[csv-wrong-field]`), а не значення.

## 6. Page Object і компоненти: що де живе

| Шар | Містить | Не містить |
| --- | --- | --- |
| `tests/` | сценарій і перевірки | локатори, логіку, «магічні» числа |
| `framework/pages`, `components` | локатори (властивості), дії-дієслова, доменні запити (`is_a_marker_centered()`) | `assert`, `expect` |
| `framework/storage.py` | доменні перевірки стану (`outside_their_field()` → список id) | залежність від UI |
| `framework/data` | літеральні дані, тексти UI (`messages.py`), еталонні файли | обчислення очікуваних результатів |

Зміна верстки виправляється в одному компоненті, зміна тексту — у `messages.py`, зміна даних —
у `test_data.py`; тести не змінюються.

## 7. Перевірки Playwright, які чекають самі (web-first)

Для UI — тільки `expect(locator)...`; вони повторюються до таймауту. Не використовувати
`assert locator.is_visible()` чи `inner_text()` у тесті. Звичайний `assert` — лише для даних
поза DOM (завантажений файл, localStorage, HTTP-відповідь), і тільки після web-first перевірки,
яка дочекалася завершення дії.

## 8. Локатори, орієнтовані на користувача

`get_by_role` / `get_by_label` з текстом інтерфейсу; CSS — лише там, де немає ролей (Leaflet).
Компонент обмежений своїм коренем (`section[aria-labelledby=...]`, `role=dialog`).

## 9. Ізоляція

Кожен тест має власний browser context і власний стан localStorage, засіяний до першого
завантаження (`open_gis_with([...])`). Тести не залежать від порядку й запускаються паралельно.

## 10. Відомі дефекти

Тест перевіряє правильну поведінку й позначений `@known_bug("BUG-xx")` (strict xfail).
Реєстр — `tests/known_bugs.py`. Виправлений баг перетворює XFAIL на падіння, і маркер прибирають.

## Джерела

* Google Testing Blog — [Don't Put Logic in Tests](https://testing.googleblog.com/2014/07/testing-on-toilet-dont-put-logic-in.html);
  *Software Engineering at Google*, розд. 12 (DAMP, not DRY; test behaviors; clear failure messages).
* Playwright — [Best Practices](https://playwright.dev/docs/best-practices): user-visible behavior,
  test isolation, user-facing locators, web-first assertions.
* Microsoft — [Unit testing best practices](https://learn.microsoft.com/dotnet/core/testing/unit-testing-best-practices):
  Arrange/Act/Assert, avoid logic in tests, avoid magic strings.
* Sourcery — [no-loop-in-tests](https://docs.sourcery.ai/Coding-Assistant/Reference/Rules-and-In-Line-Suggestions/Python/Default-Rules/no-loop-in-tests/):
  parametrize instead of loops, move complex logic into helpers and fixtures.
* [anton.qa — Page Object Model in Playwright](https://www.anton.qa/blog/posts/page-object-model-in-playwright-with-typescript-complete-guide#best-practices):
  base page, components, fixtures, assertions in tests.
