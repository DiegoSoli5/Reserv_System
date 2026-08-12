from app.main import app
from app.config import settings
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import pytest
from app import models, schemas
from app.oauth2 import create_access_token
from app.database import get_db, Base
from datetime import timedelta, timezone, datetime


# creating a database only for testing usages

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg://{settings.db_user}:{settings.db_password}@{settings.db_host}:5434/{settings.db_name}_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(session):
    def get_test_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = get_test_db
    yield TestClient(app)
    
@pytest.fixture
def test_client(client):
    client_data = {"email":"test@email.com", "password":"12345678", "role":"user"}
    res = client.post("/client/", json=client_data)
    
    new_client = res.json()
    new_client["password"] = client_data["password"]
    
    return new_client


@pytest.fixture
def test_admin_client(client):
    client_data = {"email":"test_admin@email.com", "password":"12345678", "role":"admin"}
    res = client.post("/client/", json=client_data)
    assert res.status_code == 201
    
    new_client = res.json()
    new_client["password"] = client_data["password"]
    return new_client

@pytest.fixture
def token(test_client):
    return create_access_token(data={"sub":str(test_client["id"])}, role=test_client["role"])

@pytest.fixture
def token_admin(test_admin_client):
    
    print("-"*10)
    print(test_admin_client["role"])
    print("-"*10)
    
    token = create_access_token(
        data={"sub":str(test_admin_client["id"])},
        role=test_admin_client["role"])
    
    print("-"*10)
    print(token)
    print("-"*10)
    
    return token
    

@pytest.fixture
def autClient(client, token):
    authed_client = TestClient(app)
    authed_client.headers.update({"Authorization": f"Bearer {token}"})
    return authed_client

@pytest.fixture
def autAdmin(client, token_admin):
    admin_client = TestClient(app)
    admin_client.headers.update({"Authorization": f"Bearer {token_admin}"})
    return admin_client

@pytest.fixture
def multi_clients(test_admin_client, test_client):
    clients = [test_admin_client,test_client]
    return clients

# @pytest.fixture
# def test_event(session):
#     event_data = {
#         "title":"something",
#         "description": None,
#         "date": str(datetime.now(timezone.utc) + timedelta(minutes=10)),
#         "location":"here",
#         "total_tickets":10,
#         "avaliable_tickets": 10,
#         "price":100,
#     }
#     def create_event(data):
#         return models.Event(**data)
    
#     new_event  = create_event(event_data)
#     session.add(new_event)
#     session.commit()
    
#     new_event = session.scalars(select(models.Event)).all()
#     return new_event

@pytest.fixture
def test_create_event(autAdmin):
    event_data = {
        "title":"something",
        "description": None,
        "date": str(datetime.now(timezone.utc) + timedelta(minutes=10)),
        "location":"here",
        "total_tickets":10,
        "price":100        
    }
    res = autAdmin.post("/event/", json=event_data)
    print("-"*10)
    print(res.json())
    print("-"*10)
    event_res = schemas.EventResponse(**res.json())
    new_event = res.json()
    
    return event_res

    