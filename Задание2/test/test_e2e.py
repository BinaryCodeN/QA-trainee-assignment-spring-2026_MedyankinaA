"""E2E tests"""

import requests
import allure

from conftest import BASE_URL, create_item, extract_id_from_status, random_seller_id


@allure.feature("E2E")
class TestE2E:

    @allure.title("E2E-001: Полный жизненный цикл объявления")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_full_item_lifecycle(self, seller_id):
        # 1. Create
        create_resp = create_item(seller_id=seller_id, name="E2E Laptop",
                                  price=50000, likes=10, view_count=100, contacts=5)
        assert create_resp.status_code == 200, create_resp.text
        item_id = extract_id_from_status(create_resp.json())
        assert item_id

        # 2. Get by ID
        get_resp = requests.get(f"{BASE_URL}/api/1/item/{item_id}", timeout=15)
        assert get_resp.status_code == 200
        fetched = get_resp.json()
        if isinstance(fetched, list):
            fetched = fetched[0]
        assert fetched["id"] == item_id
        assert fetched["name"] == "E2E Laptop"
        assert fetched["price"] == 50000

        # 3. In seller list
        list_resp = requests.get(f"{BASE_URL}/api/1/{seller_id}/item", timeout=15)
        assert list_resp.status_code == 200
        assert item_id in [i["id"] for i in list_resp.json()]

        # 4. Statistics
        stat_resp = requests.get(f"{BASE_URL}/api/1/statistic/{item_id}", timeout=15)
        assert stat_resp.status_code == 200
        stats = stat_resp.json()
        if isinstance(stats, list):
            stats = stats[0]
        assert stats["likes"] == 10
        assert stats["viewCount"] == 100
        assert stats["contacts"] == 5

    @allure.title("E2E-002: Изоляция данных между продавцами")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_seller_data_isolation(self):
        seller_a, seller_b = random_seller_id(), random_seller_id()

        ra = create_item(seller_id=seller_a, name="Item A")
        assert ra.status_code == 200, ra.text
        id_a = extract_id_from_status(ra.json())

        rb = create_item(seller_id=seller_b, name="Item B")
        assert rb.status_code == 200, rb.text
        id_b = extract_id_from_status(rb.json())

        ids_a = [i["id"] for i in requests.get(
            f"{BASE_URL}/api/1/{seller_a}/item", timeout=15).json()]
        ids_b = [i["id"] for i in requests.get(
            f"{BASE_URL}/api/1/{seller_b}/item", timeout=15).json()]

        assert id_a in ids_a and id_b not in ids_a
        assert id_b in ids_b and id_a not in ids_b

    @allure.title("E2E-003: Несколько объявлений одного продавца — все уникальны")
    @allure.severity(allure.severity_level.NORMAL)
    def test_multiple_items_unique_ids(self, seller_id):
        ids = []
        for i in range(3):
            r = create_item(seller_id=seller_id, name=f"Item {i}")
            assert r.status_code == 200
            ids.append(extract_id_from_status(r.json()))

        assert len(set(ids)) == 3

        fetched = [i["id"] for i in requests.get(
            f"{BASE_URL}/api/1/{seller_id}/item", timeout=15).json()]
        for cid in ids:
            assert cid in fetched