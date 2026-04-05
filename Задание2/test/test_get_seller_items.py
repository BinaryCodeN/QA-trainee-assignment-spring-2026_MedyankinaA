"""Tests for GET /api/1/:sellerID/item"""

import time
import requests
import allure

from conftest import BASE_URL, create_item, random_seller_id


@allure.feature("GET /api/1/:sellerID/item")
class TestGetSellerItems:

    @allure.title("TC-003-01: Статус 200 для существующего продавца")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_seller_items_status(self, seller_id, created_item):
        resp = requests.get(f"{BASE_URL}/api/1/{seller_id}/item", timeout=15)
        assert resp.status_code == 200, resp.text

    @allure.title("TC-003-02: Ответ — массив")
    def test_get_seller_items_is_list(self, seller_id, created_item):
        resp = requests.get(f"{BASE_URL}/api/1/{seller_id}/item", timeout=15)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    @allure.title("TC-003-03: Созданное объявление есть в списке продавца")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_created_item_in_seller_list(self, seller_id, created_item):
        resp = requests.get(f"{BASE_URL}/api/1/{seller_id}/item", timeout=15)
        assert resp.status_code == 200
        ids = [i["id"] for i in resp.json()]
        assert created_item["id"] in ids

    @allure.title("TC-003-04: Все объявления в списке принадлежат этому продавцу")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_all_items_belong_to_seller(self, seller_id, created_item):
        resp = requests.get(f"{BASE_URL}/api/1/{seller_id}/item", timeout=15)
        assert resp.status_code == 200
        for item in resp.json():
            assert item["sellerId"] == seller_id

    @allure.title("TC-003-05: Новый продавец без объявлений → 200 [] или 404")
    def test_seller_with_no_items(self):
        resp = requests.get(f"{BASE_URL}/api/1/{random_seller_id()}/item", timeout=15)
        assert resp.status_code in (200, 404)

    @allure.title("TC-003-06: sellerID строка → 400")
    def test_invalid_seller_id(self):
        resp = requests.get(f"{BASE_URL}/api/1/abc/item", timeout=15)
        assert resp.status_code == 400

    @allure.title("TC-003-07: Идемпотентность")
    def test_idempotent(self, seller_id, created_item):
        url = f"{BASE_URL}/api/1/{seller_id}/item"
        r1 = requests.get(url, timeout=15)
        r2 = requests.get(url, timeout=15)
        assert r1.status_code == r2.status_code == 200
        assert r1.json() == r2.json()

    @allure.title("TC-003-08: Время ответа < 2000 мс")
    def test_response_time(self, seller_id, created_item):
        start = time.time()
        resp = requests.get(f"{BASE_URL}/api/1/{seller_id}/item", timeout=15)
        assert resp.status_code == 200
        assert (time.time() - start) * 1000 < 2000