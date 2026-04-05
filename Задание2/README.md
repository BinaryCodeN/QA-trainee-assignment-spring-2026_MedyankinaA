# Avito QA Internship — API Test Suite

Автоматизированные тесты для микросервиса объявлений `https://qa-internship.avito.com`.

## Структура проекта

```
Задание2/
├── allure-report              # Папка с сайтом (allure generate) 
│   ├── data/                  #  данные для графиков и таблиц
│   ├── export/                # экспорт метрик
│   ├── history/               # история предыдущих прогонов
│   ├── plugin/                # плагины Allure
│   ├── widgets/               # виджеты дашборда (круговая диаграмма и др.)
│   ├── Скриншоты/             # папка со скриншотами результата работы в Allure 
│   ├── allure-example.html    # отчет работы в формате .html
│   ├── app.js
│   ├── favicon.ico
│   └── styles.css
├── allure-results             # Папка с сырыми данные (записи pytest-ов)
├── tests/
│   ├── conftest.py            # Общие фикстуры pytest
│   ├── test_create_item.py    # TC-001: POST /api/1/item
│   ├── test_get_item.py       # TC-002: GET /api/1/item/:id
│   ├── test_get_seller_items.py # TC-003: GET /api/1/:sellerID/item
│   ├── test_statistics.py     # TC-004: GET /api/1/statistic/:id
│   └── test_e2e.py            # E2E-сценарии
├── BUGS.md                    # Найденные дефекты
├── README.md
├── TESTCASES.md               # Описание всех тест-кейсов
├── pyproject.toml             # Конфигурация black / isort                  
├── pytest.ini                 # Конфигурация pytest
├── requirements.txt           # Зависимости
└── .flake8                    # Конфигурация flake8
```

## Запуск тестов

### Тесты с Allure-отчётом

```bash
# 1. Запустить тесты с сохранением результатов
pytest --alluredir=allure-results

# 2. Сгенерировать и открыть отчёт
allure serve allure-results

# 3. Сгенерировать папку allure-report со статическим HTML
allure generate allure-results --clean -o allure-report
```

### Сортировка импортов (isort)

```bash
# Проверить
isort --check-only tests/

# Применить
isort tests/
```

## Конфигурация

| Файл | Назначение |
|------|-----------|
| `pytest.ini` | Настройки pytest (testpaths, verbosity) |
| `.flake8` | Правила flake8 (max-line-length=100, игнорируемые коды) |
| `pyproject.toml` | Конфиг black (line-length=100) и isort (profile=black) |

## Принципы тестирования

- Каждый тест **независим**: использует уникальный `sellerId` через фикстуру
- Тесты **воспроизводимы**: не зависят от порядка запуска
- Используются **техники тест-дизайна**: граничные значения, классы эквивалентности, негативное тестирование, E2E
- Все проверки реализованы через **assert** с информативными сообщениями

## Покрытие тест-кейсов

| ID | Эндпоинт | Тип | Файл |
|----|----------|-----|------|
| TC-001-01..18 | POST /api/1/item | Позитивные / Негативные / Корнер-кейсы / Нефункциональные | test_create_item.py |
| TC-002-01..06 | GET /api/1/item/:id | Позитивные / Негативные / Корнер-кейсы / Нефункциональные | test_get_item.py |
| TC-003-01..06 | GET /api/1/:sellerID/item | Позитивные / Негативные / Корнер-кейсы / Нефункциональные | test_get_seller_items.py |
| TC-004-01..06 | GET /api/1/statistic/:id | Позитивные / Негативные / Корнер-кейсы / Нефункциональные | test_statistics.py |
| E2E-001..003 | Все эндпоинты | E2E | test_e2e.py |
