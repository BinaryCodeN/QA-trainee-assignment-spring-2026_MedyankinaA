"""Tests for POST /api/1/item"""

import time
import pytest
import requests
import allure

from conftest import BASE_URL, create_item, extract_id_from_status, random_seller_id


@allure.feature("POST /api/1/item")
class TestCreateItem:

    @allure.title("TC-001-01: Ответ содержит статус с UUID (формат отличается от спеки — BUG-001)")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_valid_item_returns_status_with_uuid(self, seller_id):
        payload = {
            "sellerID": seller_id,
            "name": "Bicycle",
            "price": 15000,
            "statistics": {"likes": 1, "viewCount": 2, "contacts": 3},
        }
        resp = requests.post(f"{BASE_URL}/api/1/item", json=payload, timeout=15)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "status" in data, f"No 'status' field: {data}"
        item_id = extract_id_from_status(data)
        assert item_id is not None, f"No UUID in status: {data}"

    @allure.title("TC-001-02: Повторные запросы создают объявления с разными UUID")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_returns_unique_ids(self, seller_id):
        r1 = create_item(seller_id=seller_id, name="Dup")
        r2 = create_item(seller_id=seller_id, name="Dup")
        assert r1.status_code == 200, r1.text
        assert r2.status_code == 200, r2.text
        assert extract_id_from_status(r1.json()) != extract_id_from_status(r2.json())

    @allure.title("TC-001-03: [BUG-002] price=0 → сервер возвращает 400 (ожидалось 200)")
    def test_create_item_price_zero_is_rejected(self, seller_id):
        """Баг: нулевая цена должна быть допустима, но сервер отклоняет."""
        resp = create_item(seller_id=seller_id, price=0)
        assert resp.status_code == 400  # фиксируем фактическое поведение

    @allure.title("TC-001-04: [BUG-003] name из 255 символов → 400 (лимит не задокументирован)")
    def test_create_item_long_name_is_rejected(self, seller_id):
        resp = create_item(seller_id=seller_id, name="A" * 255)
        assert resp.status_code == 400  # фиксируем фактическое поведение

    @allure.title("TC-001-05: [BUG-002] Нулевая статистика → 400 (ожидалось 200)")
    def test_create_item_zero_statistics_is_rejected(self, seller_id):
        resp = create_item(seller_id=seller_id, likes=0, view_count=0, contacts=0)
        assert resp.status_code == 400  # фиксируем фактическое поведение

    @allure.title("TC-001-06: Создание с валидными данными (ненулевая статистика)")
    def test_create_item_nonzero_statistics(self, seller_id):
        resp = create_item(seller_id=seller_id, likes=1, view_count=1, contacts=1)
        assert resp.status_code == 200, resp.text

    @allure.title("TC-001-07: sellerID на нижней границе (111111)")
    def test_create_item_seller_id_lower_bound(self):
        resp = create_item(seller_id=111111)
        assert resp.status_code == 200, resp.text

    @allure.title("TC-001-08: sellerID на верхней границе (999999)")
    def test_create_item_seller_id_upper_bound(self):
        resp = create_item(seller_id=999999)
        assert resp.status_code == 200, resp.text

    @allure.title("TC-001-09: Отсутствует поле name → 400")
    def test_create_item_missing_name(self, seller_id):
        payload = {"sellerID": seller_id, "price": 100,
                   "statistics": {"likes": 1, "viewCount": 1, "contacts": 1}}
        resp = requests.post(f"{BASE_URL}/api/1/item", json=payload, timeout=15)
        assert resp.status_code == 400

    @allure.title("TC-001-10: [BUG-004] Отсутствует sellerID → таймаут вместо 400")
    @pytest.mark.xfail(raises=requests.exceptions.ReadTimeout,
                       reason="BUG-004: сервер зависает вместо быстрого 400")
    def test_create_item_missing_seller_id(self):
        payload = {"name": "No seller", "price": 100,
                   "statistics": {"likes": 1, "viewCount": 1, "contacts": 1}}
        resp = requests.post(f"{BASE_URL}/api/1/item", json=payload, timeout=15)
        assert resp.status_code == 400

    @allure.title("TC-001-11: Отсутствует поле price → 400")
    def test_create_item_missing_price(self, seller_id):
        payload = {"sellerID": seller_id, "name": "No price",
                   "statistics": {"likes": 1, "viewCount": 1, "contacts": 1}}
        resp = requests.post(f"{BASE_URL}/api/1/item", json=payload, timeout=15)
        assert resp.status_code == 400

    @allure.title("TC-001-12: price отрицательный → 400")
    def test_create_item_negative_price(self, seller_id):
        resp = create_item(seller_id=seller_id, price=-1)
        assert resp.status_code == 400

    @allure.title("TC-001-13: price — строка → 400")
    def test_create_item_price_as_string(self, seller_id):
        payload = {"sellerID": seller_id, "name": "Bad", "price": "дорого",
                   "statistics": {"likes": 1, "viewCount": 1, "contacts": 1}}
        resp = requests.post(f"{BASE_URL}/api/1/item", json=payload, timeout=15)
        assert resp.status_code == 400

    @allure.title("TC-001-14: sellerID — строка → 400")
    def test_create_item_seller_id_as_string(self):
        payload = {"sellerID": "abc", "name": "Bad", "price": 100,
                   "statistics": {"likes": 1, "viewCount": 1, "contacts": 1}}
        resp = requests.post(f"{BASE_URL}/api/1/item", json=payload, timeout=15)
        assert resp.status_code == 400

    @allure.title("TC-001-15: Пустое тело → 400")
    def test_create_item_empty_body(self):
        resp = requests.post(f"{BASE_URL}/api/1/item", json={}, timeout=15)
        assert resp.status_code == 400

    @allure.title("TC-001-16: name — пустая строка → 400")
    def test_create_item_empty_name(self, seller_id):
        resp = create_item(seller_id=seller_id, name="")
        assert resp.status_code == 400

    @allure.title("TC-001-17: Content-Type ответа — application/json")
    def test_create_item_content_type(self, seller_id):
        resp = create_item(seller_id=seller_id)
        assert resp.status_code == 200, resp.text
        assert "application/json" in resp.headers.get("Content-Type", "")

    @allure.title("TC-001-18: [BUG-005] Время ответа > 2000 мс")
    @pytest.mark.xfail(reason="BUG-005: сервер отвечает медленнее 2 сек")
    def test_create_item_response_time(self, seller_id):
        start = time.time()
        resp = create_item(seller_id=seller_id)
        elapsed_ms = (time.time() - start) * 1000
        assert resp.status_code == 200
        assert elapsed_ms < 2000, f"Took {elapsed_ms:.0f}ms"