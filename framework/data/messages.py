"""User-facing texts of the application, in one place: a wording change is fixed here only."""

POINT_DELETED = "Точку моніторингу видалено"
DATA_RESET = "Дані успішно скинуто до початкових демо-точок"
DESCRIPTION_TOO_LONG = "Опис не повинен перевищувати 250 символів"
NO_POINTS_FOUND = "Точок за вашим запитом не знайдено"
POINT_OUTSIDE_FIELD_1 = 'Точка повинна бути в межах обраного поля "Поле №1 - Озима пшениця".'
DEMO_LOADED = "Завантажено 6 точок з еталонного мок-файлу!"
EXPORTED_5_TO_GEOJSON = "Експортовано 5 точок у GeoJSON"
EXPORTED_5_TO_CSV = "Експортовано 5 точок у CSV"

IMPORT_INVALID_JSON = "Помилка синтаксису JSON під час парсингу файлу."
IMPORT_NOT_FEATURE_COLLECTION = "Некоректний формат GeoJSON: очікується FeatureCollection з масивом features."
IMPORT_NO_POINT_FEATURES = "У GeoJSON файлі не знайдено валідних точок моніторингу."
IMPORT_CSV_HEADER_ONLY = "CSV файл повинен містити рядок заголовків та щонайменше один рядок даних."
IMPORT_CSV_NO_LAT_LNG = "У CSV не знайдено обов’язкових колонок широти (Lat) та довготи (Lng)."
IMPORT_CSV_NO_VALID_ROWS = "У CSV файлі не знайдено валідних рядків з координатами."
