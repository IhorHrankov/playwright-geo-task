# Чек-лист

Застосунок: AgTech Fields GIS, `/#/test` · Chrome (desktop) · 31.10.2026

**36 перевірок: 22 Pass, 14 Fail.** Пункти 3, 4, 7, 18, 19 вручну перевірено частково,
решту підтверджено аналізом коду. Усі вони покриті автотестами (стовпець «Автотест»).

| # | Область | Перевірка | Результат | Баг | Автотест |
| --- | --- | --- | --- | --- | --- |
| 1 | Поля | Список показує 4 поля з назвою, площею, культурою, кількістю точок | Pass | | `test_fields::test_all_fields_are_listed_with_area_and_crop` |
| 2 | Поля | Перше поле активне за замовчуванням, карта центрована на ньому | Pass | | `test_fields::test_first_field_is_active_by_default` |
| 3 | Поля | Клік по картці поля робить його активним і центрує карту | Pass | | `test_fields::test_select_field_from_list` |
| 4 | Поля | Клік по неактивному полігону на карті робить поле активним | Pass | | `test_fields::test_select_field_by_clicking_its_polygon` |
| 5 | Поля | Площа поля відповідає геометрії полігона | **Fail** | BUG-08 | `test_fields::test_displayed_area_matches_polygon_geometry` |
| 6 | Поля | Лічильник точок у картці поля відповідає реальній кількості | Pass | | `test_fields::test_field_points_counter_matches_data` |
| 7 | Поля | Картка поля доступна з клавіатури (Tab, Enter, Space) | Pass | | — (код: `tabIndex=0`, onKeyDown) |
| 8 | Карта | Підкладка «Схема» відображає картографічну основу | **Fail** | BUG-07 | `test_map::test_streets_basemap_tiles_are_real_map_images`, `api/test_basemap_tiles` |
| 9 | Карта | Підкладка «Супутник» відображає знімки | Pass | | `test_map::test_switch_to_satellite_and_back` |
| 10 | Карта | «Сфокусувати активне поле» повертає карту до поля | Pass | | `test_map::test_focus_button_returns_to_active_field` |
| 11 | Карта | Tooltip полігона: назва, площа, культура | Pass | | `test_fields::test_field_tooltip_shows_name_area_and_crop` |
| 12 | Карта | Колір та іконка маркера відповідають типу | Pass | | — (візуально) |
| 13 | Карта | Фільтр/пошук впливає на маркери на карті | **Fail** | BUG-11 | `test_points_list::test_type_filter_is_applied_to_map_markers` |
| 14 | Додавання | Клік усередині активного поля відкриває модалку з Lat/Lng і MGRS | Pass | | `test_add_point::test_add_point_inside_active_field` |
| 15 | Додавання | MGRS у модалці відповідає координатам кліку | Pass | | там само (незалежний оракул) |
| 16 | Додавання | Клік поза активним полем показує помилку з назвою поля | Pass | | `test_add_point::test_click_outside_active_field_is_rejected` |
| 17 | Додавання | Збереження додає точку на початок списку і на карту | Pass | | `test_add_point::test_added_point_appears_on_map` |
| 18 | Додавання | Опис понад 250 символів блокує збереження з повідомленням | Pass | | `test_add_point::test_description_length_limit` |
| 19 | Додавання | «Скасувати» / Esc / хрестик закривають модалку без збереження | Pass | | `test_add_point::test_closing_modal_does_not_create_point` |
| 20 | Збереження | Точки зберігаються після перезавантаження сторінки | Pass | | `test_add_point::test_added_point_persists_after_reload` |
| 21 | Видалення | Видалення зі списку та з попапу прибирає лише одну точку | **Fail** | BUG-03 | `test_import::test_duplicate_ids_corrupt_list_and_delete` |
| 22 | Видалення | Видалення потребує підтвердження або дає скасувати дію | **Fail** | BUG-14 | `test_points_list::test_delete_asks_for_confirmation` |
| 23 | Пошук | Пошук за описом, MGRS, назвою поля, типом (без урахування регістру) | Pass | | `test_points_list::test_search*` |
| 24 | Фільтр | Чипи типів фільтрують список; «Всі» скидає фільтр | Pass | | `test_points_list::test_filter_by_type` |
| 25 | Фільтр | Порожній результат показує «Скинути фільтри» | Pass | | `test_points_list::test_search_without_results_offers_filter_reset` |
| 26 | Сортування | «Нові/Старі» сортує за датою створення | **Fail** | BUG-04 | `test_points_list::test_sort_toggle_*`, `test_import::test_invalid_created_at_is_rejected` |
| 27 | Навігація | «Показати на карті» центрує карту на точці при кожному кліку | **Fail** | BUG-10 | `test_points_list::test_show_on_map_twice_recentres_after_pan` |
| 28 | Експорт | GeoJSON: FeatureCollection з Point, [lng, lat], усі властивості | Pass | | `test_export::test_export_geojson` |
| 29 | Експорт | CSV: UTF-8 BOM, роздільник «;», екранування лапок | Pass | | `test_export::test_export_csv`, `test_csv_escapes_quotes_and_delimiters` |
| 30 | Експорт | CSV безпечний для Excel (формули не виконуються) | **Fail** | BUG-09 | `test_export::test_csv_neutralises_formulas` |
| 31 | Експорт | Обсяг експорту зрозумілий користувачу (усі чи відфільтровані) | **Fail** | BUG-12 | `test_export::test_export_contains_all_points_even_when_list_is_filtered` |
| 32 | Імпорт | Повторний імпорт того ж файлу не створює дублікатів | **Fail** | BUG-06 | `test_import::test_reimport_of_exported_file_does_not_duplicate` |
| 33 | Імпорт | Точки поза межами полів відхиляються | **Fail** | BUG-01 | `test_import::test_points_outside_their_field_are_rejected` |
| 34 | Імпорт | Невалідні координати (lat > 90, lng > 180) відхиляються | **Fail** | BUG-02 | `test_import::test_out_of_range_coordinates_are_rejected` |
| 35 | Імпорт | MGRS із файлу перевіряється або перераховується | **Fail** | BUG-05 | `test_import::test_imported_mgrs_is_recalculated` |
| 36 | Імпорт | Повідомлення про результат граматично коректне | **Fail** | BUG-13 | `test_import::test_toast_uses_correct_plural_for_one_point` |

## Додаткові перевірки (лише автотести)

| Область | Перевірка | Результат | Автотест |
| --- | --- | --- | --- |
| HTTP | Без Basic Auth — 401 + `WWW-Authenticate: Basic`; з неправильним паролем — 401 | Pass | `api/test_auth_and_static` |
| HTTP | Security-заголовки (HSTS, nosniff, X-Frame-Options, CSP) | **Fail** (BUG-16) | `api/test_auth_and_static::test_security_headers_present` |
| HTTP | Контракт demo-GeoJSON: схема, унікальні id, точки всередині полів, MGRS | Pass | `api/test_sample_data_contract` |
| Імпорт | Пошкоджені файли (JSON, не FeatureCollection, CSV без Lat/Lng тощо) відхиляються з повідомленням | Pass | `test_import::test_malformed_file_is_rejected` |
| Старт | Невідомий hash-маршрут веде на стартову сторінку | Pass | `test_start_page` |
| Старт | Унікальні `id` елементів | **Fail** (BUG-15) | `test_start_page::test_start_page_has_unique_element_ids` |
