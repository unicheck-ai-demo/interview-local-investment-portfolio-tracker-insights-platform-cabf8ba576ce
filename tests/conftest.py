from typing import Any

import pytest
from rest_framework.test import APIClient

from app.models import User


@pytest.fixture
def user(db: Any) -> User:
    return User.objects.create_user(username='testuser', password='password123', role='investor')


@pytest.fixture
def api_client() -> APIClient:
    client = APIClient()
    return client


@pytest.fixture
def authenticated_api_client(user: User, api_client: APIClient) -> APIClient:
    api_client.force_authenticate(user)
    return api_client
