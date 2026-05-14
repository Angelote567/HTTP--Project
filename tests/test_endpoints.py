from __future__ import annotations

import json

from usj_http.client import HTTPClient


def parse_json(response) -> dict:
    return json.loads(response.body.decode("utf-8"))


def test_static_index(base_url, client):
    _, response = client.request("GET", f"{base_url}/index.html")
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("text/html")
    assert b"<html" in response.body.lower()


def test_cats_crud_lifecycle(base_url, client):
    _, response = client.request("GET", f"{base_url}/cats")
    assert response.status_code == 200
    initial_count = len(parse_json(response)["items"])

    _, created = client.request(
        "POST",
        f"{base_url}/cats",
        extra_headers={"Content-Type": "application/json"},
        body_text=json.dumps({"name": "Milo", "breed": "Tabby", "age": 4}),
    )
    assert created.status_code == 201
    new_cat = parse_json(created)
    assert new_cat["name"] == "Milo"
    cat_id = new_cat["id"]
    assert created.headers["Location"] == f"/cats/{cat_id}"

    _, listed = client.request("GET", f"{base_url}/cats")
    assert len(parse_json(listed)["items"]) == initial_count + 1

    _, fetched = client.request("GET", f"{base_url}/cats/{cat_id}")
    assert fetched.status_code == 200
    assert parse_json(fetched)["name"] == "Milo"

    _, updated = client.request(
        "PUT",
        f"{base_url}/cats/{cat_id}",
        extra_headers={"Content-Type": "application/json"},
        body_text=json.dumps({"name": "Milo", "breed": "Tabby", "age": 5}),
    )
    assert updated.status_code == 200
    assert parse_json(updated)["age"] == 5

    _, deleted = client.request("DELETE", f"{base_url}/cats/{cat_id}")
    assert deleted.status_code == 204
    assert deleted.body == b""

    _, missing = client.request("GET", f"{base_url}/cats/{cat_id}")
    assert missing.status_code == 404


def test_cats_validation(base_url, client):
    _, response = client.request(
        "POST",
        f"{base_url}/cats",
        extra_headers={"Content-Type": "application/json"},
        body_text="{ this is not json",
    )
    assert response.status_code == 400

    _, response = client.request(
        "POST",
        f"{base_url}/cats",
        extra_headers={"Content-Type": "application/json"},
        body_text=json.dumps({"name": "X"}),
    )
    assert response.status_code == 400


def test_method_not_allowed(base_url, client):
    _, response = client.request("PATCH", f"{base_url}/cats")
    assert response.status_code == 405
    assert "GET" in response.headers["Allow"]


def test_owners_and_nested_cats(base_url, client):
    _, owners = client.request("GET", f"{base_url}/owners")
    assert owners.status_code == 200
    owner_id = parse_json(owners)["items"][0]["id"]

    _, nested = client.request("GET", f"{base_url}/owners/{owner_id}/cats")
    assert nested.status_code == 200
    items = parse_json(nested)["items"]
    assert all(item["owner_id"] == owner_id for item in items)


def test_owner_deletion_cascades(base_url, client):
    _, created = client.request(
        "POST",
        f"{base_url}/owners",
        extra_headers={"Content-Type": "application/json"},
        body_text=json.dumps({"name": "Test", "email": "test@example.com"}),
    )
    new_owner_id = parse_json(created)["id"]

    _, _ = client.request(
        "POST",
        f"{base_url}/cats",
        extra_headers={"Content-Type": "application/json"},
        body_text=json.dumps({"name": "Pelusa", "breed": "Persian", "age": 1, "owner_id": new_owner_id}),
    )

    _, before = client.request("GET", f"{base_url}/owners/{new_owner_id}/cats")
    assert len(parse_json(before)["items"]) == 1

    _, deleted = client.request("DELETE", f"{base_url}/owners/{new_owner_id}")
    assert deleted.status_code == 204

    _, after = client.request("GET", f"{base_url}/owners/{new_owner_id}")
    assert after.status_code == 404


def test_cookies_round_trip(base_url, client):
    _, first = client.request("GET", f"{base_url}/session")
    assert first.status_code == 200
    assert any("usj_session" in c for c in first.set_cookies)
    assert parse_json(first)["visits"] == 0

    _, second = client.request("GET", f"{base_url}/session")
    assert parse_json(second)["visits"] == 2


def test_api_key_required(secured_setup):
    base_url, api_key = secured_setup

    no_key = HTTPClient()
    _, response = no_key.request("GET", f"{base_url}/cats")
    assert response.status_code == 401

    authed = HTTPClient(api_key=api_key)
    _, ok = authed.request("GET", f"{base_url}/cats")
    assert ok.status_code == 200

    _, static_no_key = no_key.request("GET", f"{base_url}/index.html")
    assert static_no_key.status_code == 200
