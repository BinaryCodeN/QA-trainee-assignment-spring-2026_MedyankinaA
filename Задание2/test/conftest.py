"""Shared fixtures and configuration for pytest."""

import re
import random
import pytest
import requests

BASE_URL = "https://qa-internship.avito.com"

_STATUS_UUID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
)


def extract_id_from_status(response_json: dict) -> str | None:
    """Извлечь UUID из поля status: 'Сохранили объявление - <uuid>'"""
    status = response_json.get("status", "")
    match = _STATUS_UUID_RE.search(status)
    return match.group(0) if match else None


def random_seller_id() -> int:
    return random.randint(111111, 999999)


def create_item(
    seller_id: int = None,
    name: str = "Test item",
    price: int = 500,
    likes: int = 1,
    view_count: int = 1,
    contacts: int = 1,
) -> requests.Response:
    if seller_id is None:
        seller_id = random_seller_id()
    payload = {
        "sellerID": seller_id,
        "name": name,
        "price": price,
        "statistics": {
            "likes": likes,
            "viewCount": view_count,
            "contacts": contacts,
        },
    }
    return requests.post(f"{BASE_URL}/api/1/item", json=payload, timeout=15)


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture
def seller_id():
    return random_seller_id()


@pytest.fixture
def created_item(seller_id):
    resp = create_item(seller_id=seller_id, name="Fixture item", price=999,
                       likes=5, view_count=10, contacts=3)
    assert resp.status_code == 200, f"Fixture failed: {resp.text}"
    item_id = extract_id_from_status(resp.json())
    assert item_id, f"No UUID in: {resp.json()}"
    return {
        "id": item_id,
        "sellerId": seller_id,
        "name": "Fixture item",
        "price": 999,
        "statistics": {"likes": 5, "viewCount": 10, "contacts": 3},
    }