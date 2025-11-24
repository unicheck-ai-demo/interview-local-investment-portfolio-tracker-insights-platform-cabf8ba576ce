import pytest
from django.contrib.gis.geos import Point

from app.models import Asset, Institution, Portfolio, Transaction, User


@pytest.mark.django_db
def test_institution_geopoint():
    location = Point(10, 20)
    inst = Institution.objects.create(name='Bank X', type=Institution.TYPE_BANK, location=location)
    assert inst.location.x == 10 and inst.location.y == 20
    assert inst.type == Institution.TYPE_BANK


@pytest.mark.django_db
def test_portfolio_and_asset_relationship():
    user = User.objects.create_user(username='userA', password='pass', role=User.ROLE_INVESTOR)
    inst = Institution.objects.create(name='Broker Y', type=Institution.TYPE_BROKER, location=Point(1, 2))
    asset = Asset.objects.create(name='Stock A', asset_type=Asset.TYPE_STOCK, institution=inst)
    portfolio = Portfolio.objects.create(user=user, name='Growth')
    trans = Transaction.objects.create(
        portfolio=portfolio, asset=asset, trans_type='buy', amount=10, price=100, date='2024-06-01T00:00:00Z'
    )
    assert asset in inst.assets.all()
    assert portfolio.user == user
    assert trans.asset == asset
    assert trans.portfolio == portfolio
