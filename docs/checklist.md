# Чек-лист

Застосунок: AgTech Fields GIS, `/#/test` · Chrome (desktop) · 31.10.2026

**36 перевірок: 22 Pass, 14 Fail.** Пункти 3, 4, 7, 18, 19 вручну перевірено частково,
решту підтверджено аналізом коду. Усі вони покриті автотестами (стовпець «Автотест»).

| # | Область | Перевірка | Результат | Баг | Автотест |
| --- | --- | --- | --- | --- | --- |
| 1 | Поля | Список показує 4 поля з назвою, площею, культурою, кількістю точок | Pass | | `test_fields::test_fields_list_shows_four_fields` |
| 2 | Поля | Перше поле активне за замовчуванням, карта центрована на ньому | Pass | | `test_fields::test_first_field_is_active_by_default` |
| 3 | Поля | Клік по картці поля робить його активним і центрує карту | Pass | | `test_fields::test_selecting_field_in_list_makes_it_the_only_active_one` |
| 4 | Поля | Клік по неактивному полігону на карті робить поле активним | Pass | | `test_fields::test_clicking_inactive_field_on_map_selects_it_without_adding_point` |
| 5 | Поля | Площа поля відповідає геометрії полігона | **Fail** | BUG-08 | `test_fields::test_field_area_matches_polygon_geometry` |
| 6 | Поля | Лічильник точок у картці поля відповідає реальній кількості | Pass | | `test_fields::test_field_card_counts_its_points` |
| 7 | Поля | Картка поля доступна з клавіатури (Tab, Enter, Space) | Pass | | — (код: `tabIndex=0`, onKeyDown) |
| 8 | Карта | Підкладка «Схема» відображає картографічну основу | **Fail** | BUG-07 | `test_map::test_streets_basemap_does_not_show_api_key_placeholder` |
| 9 | Карта | Підкладка «Супутник» відображає знімки | Pass | | `test_map::test_satellite_basemap_loads_satellite_tiles` |
| 10 | Карта | «Сфокусувати активне поле» повертає карту до поля | Pass | | `test_map::test_focus_button_returns_map_to_active_field` |
| 11 | Карта | Tooltip полігона: назва, площа, культура | Pass | | `test_fields::test_hovering_field_shows_tooltip_with_name_area_and_crop` |
| 12 | Карта | Колір та іконка маркера відповідають типу | Pass | | — (візуально) |
| 13 | Карта | Фільтр/пошук впливає на маркери на карті | **Fail** | BUG-11 | `test_points_list::test_type_filter_is_applied_to_map_markers` |
| 14 | Додавання | Клік усередині активного поля відкриває модалку з Lat/Lng і MGRS | Pass | | `test_add_point::test_saved_point_is_listed_first_with_its_details` |
| 15 | Додавання | MGRS у модалці відповідає координатам кліку | Pass | | `test_add_point::test_modal_mgrs_corresponds_to_shown_coordinates` |
| 16 | Додавання | Клік поза активним полем показує помилку з назвою поля | Pass | | `test_add_point::test_click_outside_active_field_shows_error_instead_of_modal` |
| 17 | Додавання | Збереження додає точку на початок списку і на карту | Pass | | `test_add_point::test_saved_point_appears_on_map` |
| 18 | Додавання | Опис понад 250 символів блокує збереження з повідомленням | Pass | | `test_add_point::test_description_of_251_characters_is_rejected` |
| 19 | Додавання | «Скасувати» / Esc / хрестик закривають модалку без збереження | Pass | | `test_add_point::test_cancel_button_closes_modal_without_saving` |
| 20 | Збереження | Точки зберігаються після перезавантаження сторінки | Pass | | `test_add_point::test_saved_point_survives_page_reload` |
| 21 | Видалення | Видалення зі списку та з попапу прибирає лише одну точку | **Fail** | BUG-03 | `test_import::test_deleting_one_of_duplicated_points_keeps_the_other` |
| 22 | Видалення | Видалення потребує підтвердження або дає скасувати дію | **Fail** | BUG-14 | `test_points_list::test_deleting_point_offers_undo` |
| 23 | Пошук | Пошук за описом, MGRS, назвою поля, типом (без урахування регістру) | Pass | | `test_points_list::test_search_finds_points` |
| 24 | Фільтр | Чипи типів фільтрують список; «Всі» скидає фільтр | Pass | | `test_points_list::test_type_filter_keeps_only_that_type` |
| 25 | Фільтр | Порожній результат показує «Скинути фільтри» | Pass | | `test_points_list::test_reset_filters_button_clears_search` |
| 26 | Сортування | «Нові/Старі» сортує за датою створення | **Fail** | BUG-04 | `test_points_list::test_sort_toggle_shows_oldest_first`, `test_import::test_invalid_creation_date_is_not_imported` |
| 27 | Навігація | «Показати на карті» центрує карту на точці при кожному кліку | **Fail** | BUG-10 | `test_points_list::test_show_on_map_again_after_panning_recentres_map` |
| 28 | Експорт | GeoJSON: FeatureCollection з Point, [lng, lat], усі властивості | Pass | | `test_export::test_geojson_export_matches_expected_file` |
| 29 | Експорт | CSV: UTF-8 BOM, роздільник «;», екранування лапок | Pass | | `test_export::test_csv_export_matches_expected_file`, `test_csv_export_escapes_quotes_and_semicolons` |
| 30 | Експорт | CSV безпечний для Excel (формули не виконуються) | **Fail** | BUG-09 | `test_export::test_csv_export_neutralises_spreadsheet_formulas` |
| 31 | Експорт | Обсяг експорту зрозумілий користувачу (усі чи відфільтровані) | **Fail** | BUG-12 | `test_export::test_export_contains_all_points_even_when_list_is_filtered` |
| 32 | Імпорт | Повторний імпорт того ж файлу не створює дублікатів | **Fail** | BUG-06 | `test_import::test_reimporting_exported_file_does_not_duplicate_points` |
| 33 | Імпорт | Точки поза межами полів відхиляються | **Fail** | BUG-01 | `test_import::test_point_outside_its_field_is_not_imported` |
| 34 | Імпорт | Невалідні координати (lat > 90, lng > 180) відхиляються | **Fail** | BUG-02 | `test_import::test_out_of_range_coordinates_are_not_imported` |
| 35 | Імпорт | MGRS із файлу перевіряється або перераховується | **Fail** | BUG-05 | `test_import::test_imported_mgrs_is_recalculated_from_coordinates` |
| 36 | Імпорт | Повідомлення про результат граматично коректне | **Fail** | BUG-13 | `test_import::test_import_toast_uses_singular_for_one_point` |

## Додаткові перевірки

| Область | Перевірка | Результат | Автотест |
| --- | --- | --- | --- |
| HTTP | Security-заголовки (HSTS, nosniff, X-Frame-Options, CSP) | **Fail** (BUG-16) | — (вручну) |
| Імпорт | Пошкоджені файли (JSON, не FeatureCollection, CSV без Lat/Lng тощо) відхиляються з повідомленням | Pass | `test_import::test_malformed_file_is_rejected_with_message` |
