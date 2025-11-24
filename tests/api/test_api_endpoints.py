import pytest
from django.contrib.gis.geos import Point
from django.urls import reverse
from rest_framework import status

from app.models import Asset, Institution, Portfolio, User

pytestmark = pytest.mark.django_db


def test_user_list(api_client):
    User.objects.create_user(username='x', password='pw', role='investor')
    url = reverse('api:user-list')
    resp = api_client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    assert any(u['username'] == 'x' for u in resp.data['results'])


def test_institution_create(authenticated_api_client):
    url = reverse('api:institution-list')
    data = {
        'name': 'GeoBank',
        'type': 'bank',
        'location': {'type': 'Point', 'coordinates': [14.44, 50.09]},
    }
    resp = authenticated_api_client.post(url, data, format='json')
    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.data['name'] == 'GeoBank'


def test_institution_nearest(authenticated_api_client):
    Institution.objects.create(name='Branch1', type='bank', location=Point(14.44, 50.09, srid=4326))
    url = reverse('api:institution-nearest') + '?lat=50.09&lon=14.44&radius=5'
    resp = authenticated_api_client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    assert any(i['name'] == 'Branch1' for i in resp.data)


def test_portfolio_performance(authenticated_api_client):
    user = User.objects.create_user(username='z', password='pw', role='investor')
    port = Portfolio.objects.create(user=user, name='XPort')
    url = reverse('api:portfolio-performance', args=[port.id])
    resp = authenticated_api_client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    assert 'avg_price' in resp.data


def test_transaction_multi_step(authenticated_api_client):
    user = User.objects.create_user(username='txuser', password='pw', role='investor')
    inst = Institution.objects.create(name='Exch1', type='broker', location=Point(11.1, 22.2, srid=4326))
    asset = Asset.objects.create(name='Asset1', asset_type='stock', institution=inst)
    port = Portfolio.objects.create(user=user, name='PortX')
    url = reverse('api:transaction-multi-step')
    data = {
        'portfolio': port.id,
        'asset': asset.id,
        'trans_type': 'buy',
        'amount': 101,
        'price': 999.88,
        'date': '2024-06-03T10:00:00Z',
    }
    resp = authenticated_api_client.post(url, data, format='json')
    assert resp.status_code == status.HTTP_201_CREATED
    assert str(resp.data['amount']).startswith('101')
