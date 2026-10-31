# test_data

Файли, використані під час ручного тестування й в автотестах. Опис кожного файлу, баг,
який він відтворює, і фактичний результат імпорту — у [docs/test-data.md](../docs/test-data.md).

* `state/initial_localstorage_demo.json` — вміст localStorage (`agtech_monitoring_points_v1`) до тестування.
* `state/fields.geojson` — геометрія та атрибути 4 полів застосунку.
* `import/*.csv`, `import/*.geojson` — файли для імпорту (негативні сценарії BUG-01…05, BUG-09).
