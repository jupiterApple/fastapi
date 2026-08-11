import fakeredis
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.api.deps import get_cache, get_db
from app.db.base_class import Base

_test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # garante que todas as conexões usam o mesmo BD in-memory
)
TestingSessionLocal = sessionmaker(bind=_test_engine)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=_test_engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=_test_engine)


@pytest.fixture
def cache():
    return fakeredis.FakeStrictRedis(decode_responses=True)


@pytest.fixture
def client(db, cache):
    # Suspende on_startup (conectaria ao MySQL) — tabelas já criadas pelo fixture db
    saved_startup = app.router.on_startup[:]
    app.router.on_startup.clear()

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_cache] = lambda: cache
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    app.router.on_startup.extend(saved_startup)
