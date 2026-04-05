"""Tests for GET /api/1/item/:id"""

import time
import requests
import allure

from conftest import BASE_URL


@allure.feature("GET /api/1/item/:id")
class TestGetItem:

    @allure.title("TC-002-01: Получение существующего объявления — статус 200")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_existing_item(self, created_item):
        resp = requests.get(f"{BASE_URL}/api/1/item/{created_item['id']}", timeout=15)
        assert resp.status_code == 200, resp.text

    @allure.title("TC-002-02: Ответ содержит обязательные поля")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_item_required_fields(self, created_item):
        resp = requests.get(f"{BASE_URL}/api/1/item/{created_item['id']}", timeout=15)
        assert resp.status_code == 200
        data = resp.json()
        item = data[0] if isinstance(data, list) else data
        for field in ("id", "sellerId", "name", "price", "statistics", "createdAt"):
            assert field in item, f"Missing field: {field}"

    @allure.title("TC-002-03: Данные совпадают с переданными при создании")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_item_data_matches(self, created_item):
        resp = requests.get(f"{BASE_URL}/api/1/item/{created_item['id']}", timeout=15)
        assert resp.status_code == 200
        data = resp.json()
        item = data[0] if isinstance(data, list) else data
        assert item["id"] == created_item["id"]
        assert item["name"] == created_item["name"]
        assert item["price"] == created_item["price"]
        assert item["sellerId"] == created_item["sellerId"]

    @allure.title("TC-002-04: Несуществующий UUID → 404")
    def test_get_nonexistent_item(self):
        resp = requests.get(
            f"{BASE_URL}/api/1/item/00000000-0000-0000-0000-000000000000", timeout=15)
        assert resp.status_code == 404

    @allure.title("TC-002-05: Невалидный ID → 400 или 404")
    def test_get_item_invalid_id(self):
        resp = requests.get(f"{BASE_URL}/api/1/item/not-a-valid-id", timeout=15)
        assert resp.status_code in (400, 404)

    @allure.title("TC-002-06: Идемпотентность — два GET дают одинаковый ответ")
    def test_get_item_idempotent(self, created_item):
        url = f"{BASE_URL}/api/1/item/{created_item['id']}"
        r1 = requests.get(url, timeout=15)
        r2 = requests.get(url, timeout=15)
        assert r1.status_code == r2.status_code == 200
        assert r1.json() == r2.json()

    @allure.title("TC-002-07: Время ответа < 2000 мс")
    def test_get_item_response_time(self, created_item):
        start = time.time()
        resp = requests.get(f"{BASE_URL}/api/1/item/{created_item['id']}", timeout=15)
        assert resp.status_code == 200
        assert (time.time() - start) * 1000 < 2000