from fastapi.testclient import TestClient


def test_api(client: TestClient):
    username = "bob"
    password = "pass"

    response = client.post(
        "/users",
        json={
            "username": username,
            "password": password,
        },
    )
    assert response.status_code == 201

    response = client.post(
        "/token",
        data={
            "username": username,
            "password": password,
        },
    )
    assert response.status_code == 200
    token = response.json().get("access_token")
    assert token

    response = client.post("/wallets", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201

    response = client.post(
        "/addresses",
        headers={"Authorization": f"Bearer {token}"},
        json={"currency": "BTC"},
    )
    assert response.status_code == 201
    address_id = response.json().get("id")
    assert address_id

    response = client.get(
        f"/addresses/{address_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    response = client.get("/addresses", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1
