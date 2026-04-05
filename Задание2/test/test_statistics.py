"""Tests for GET /api/1/statistic/:id"""

import time
import requests
import allure

from conftest import BASE_URL, create_item, extract_id_from_status


@allure.feature("GET /api/1/statistic/:id")
class TestGetStatistics:

    @allure.title("TC-004-01: Статус 200 для существующего объявления")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_statistics_status(self, created_item):
        resp = requests.get(f"{BASE_URL}/api/1/statistic/{created_item['id']}", timeout=15)
        assert resp.status_code == 200, resp.text

    @allure.title("TC-004-02: Ответ содержит поля likes, viewCount, contacts")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_statistics_required_fields(self, created_item):
        resp = requests.get(f"{BASE_URL}/api/1/statistic/{created_item['id']}", timeout=15)
        assert resp.status_code == 200
        stats = resp.json()
        if isinstance(stats, list):
            stats = stats[0]
        for field in ("likes", "viewCount", "contacts"):
            assert field in stats

    @allure.title("TC-004-03: Статистика совпадает с данными при создании")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_statistics_match_created_data(self, seller_id):
        resp = create_item(seller_id=seller_id, likes=5, view_count=10, contacts=3)
        assert resp.status_code == 200, resp.text
        item_id = extract_id_from_status(resp.json())
        assert item_id

        stat_resp = requests.get(f"{BASE_URL}/api/1/statistic/{item_id}", timeout=15)
        assert stat_resp.status_code == 200
        stats = stat_resp.json()
        if isinstance(stats, list):
            stats = stats[0]
        assert stats["likes"] == 5
        assert stats["viewCount"] == 10
        assert stats["contacts"] == 3

    @allure.title("TC-004-04: Несуществующий UUID → 404")
    def test_get_statistics_nonexistent(self):
        resp = requests.get(
            f"{BASE_URL}/api/1/statistic/00000000-0000-0000-0000-000000000000", timeout=15)
        assert resp.status_code == 404

    @allure.title("TC-004-05: Невалидный ID → 400 или 404")
    def test_get_statistics_invalid_id(self):
        resp = requests.get(f"{BASE_URL}/api/1/statistic/invalid-id", timeout=15)
        assert resp.status_code in (400, 404)

    @allure.title("TC-004-06: Идемпотентность")
    def test_idempotent(self, created_item):
        url = f"{BASE_URL}/api/1/statistic/{created_item['id']}"
        r1 = requests.get(url, timeout=15)
        r2 = requests.get(url, timeout=15)
        assert r1.status_code == r2.status_code == 200
        assert r1.json() == r2.json()

    @allure.title("TC-004-07: Время ответа < 2000 мс")
    def test_response_time(self, created_item):
        start = time.time()
        resp = requests.get(f"{BASE_URL}/api/1/statistic/{created_item['id']}", timeout=15)
        assert resp.status_code == 200
        assert (time.time() - start) * 1000 < 2000