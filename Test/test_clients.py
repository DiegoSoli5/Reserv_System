
from app import schemas
import jwt
from app.config import settings
import pytest

def test_create_client(client):
    res = client.post("/client/", json={"email":"test@email.com", "password":"12345678", "role":"user"})
    print(res.json())
    new_client = schemas.ClientResponse(**res.json())
    assert res.status_code == 201
    assert new_client.email == "test@email.com"
    
def test_login(client, test_client): 
    res = client.post("/login/", data={"username":test_client["email"], "password":test_client["password"]})
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token, settings.secret_key, algorithms=[settings.algorithm])
    id = payload.get("sub")
    assert res.status_code == 200
    assert int(id) == test_client["id"]
    assert login_res.token_type == "bearer"

def test_delete_self_client(autClient, test_client):
    res = autClient.delete(f"/client/{test_client["id"]}")
    assert res.status_code == 204
    
@pytest.mark.parametrize("id", [("1"), ("2")])
def test_delete_client(autAdmin, multi_clients, id):
    res = autAdmin.delete(f"/client/{id}")
    assert res.status_code == 204