from fastapi.testclient import TestClient

from zwallet.wallets.models import Address


def test_create_wallet(
    client: TestClient, token_no_wallet: str, username_no_wallet: str
) -> None:
    response = client.post(
        "/wallets", headers={"Authorization": f"Bearer {token_no_wallet}"}
    )

    assert response.status_code == 201
    assert set(response.json().keys()) == {"username", "mnemonic"}
    assert response.json().get("username") == username_no_wallet


def test_create_repeated_wallet(client: TestClient, token: str) -> None:
    response = client.post("/wallets", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 422
    assert "detail" in response.json()


def test_create_address(client: TestClient, token: str, username: str) -> None:
    response = client.post(
        "/addresses",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "currency": "BTC",
        },
    )

    assert response.status_code == 201
    assert set(response.json().keys()) == {
        "address",
        "currency",
        "id",
        "index",
        "username",
    }
    assert response.json().get("username") == username


def test_create_address_for_unsupported_currency(
    client: TestClient, token: str
) -> None:
    response = client.post(
        "/addresses",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "currency": "unsupported_currency",
        },
    )

    assert response.status_code == 422
    assert "detail" in response.json()


def test_create_address_for_user_without_wallet(
    client: TestClient, token_no_wallet: str
) -> None:
    response = client.post(
        "/addresses",
        headers={"Authorization": f"Bearer {token_no_wallet}"},
        json={
            "currency": "BTC",
        },
    )

    assert response.status_code == 422
    assert "detail" in response.json()


def test_list_addresses(address: Address, client: TestClient, token: str) -> None:
    response = client.get(
        "/addresses",
        headers={"Authorization": f"Bearer {token}"},
    )

    print(response.json())
    assert response.status_code == 200
    assert response.json() == [address.dict()]


def test_get_address(address: Address, client: TestClient, token: str) -> None:
    response = client.get(
        f"/addresses/{address.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == address.dict()


def test_unauth_get_address(
    client: TestClient, token: str, unauth_address: Address
) -> None:
    response = client.get(
        f"/addresses/{unauth_address.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


def test_get_address_not_found(client: TestClient, token: str) -> None:
    response = client.get(
        "/addresses/1000",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
