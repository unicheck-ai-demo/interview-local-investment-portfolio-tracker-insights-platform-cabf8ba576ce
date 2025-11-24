import pytest
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point

from app.models import Asset, Institution, Portfolio, Transaction
from app.services import PortfolioService

pytestmark = pytest.mark.django_db


@pytest.mark.xfail(strict=True)
def test_portfolio_holdings_breakdown():
    User = get_user_model()
    user = User.objects.create_user(username='u', password='p', role='investor')
    inst = Institution.objects.create(name='Inst', type=Institution.TYPE_BANK, location=Point(0, 0, srid=4326))
    asset1 = Asset.objects.create(name='AssetA', asset_type=Asset.TYPE_STOCK, institution=inst)
    asset2 = Asset.objects.create(name='AssetB', asset_type=Asset.TYPE_BOND, institution=inst)
    portfolio = Portfolio.objects.create(user=user, name='P1')
    Transaction.objects.create(
        portfolio=portfolio, asset=asset1, trans_type='buy', amount=10, price=5, date='2024-01-01T00:00:00Z'
    )
    Transaction.objects.create(
        portfolio=portfolio, asset=asset2, trans_type='buy', amount=5, price=20, date='2024-01-02T00:00:00Z'
    )
    Transaction.objects.create(
        portfolio=portfolio, asset=asset1, trans_type='buy', amount=20, price=7, date='2024-01-03T00:00:00Z'
    )

    holdings = PortfolioService.get_holdings(portfolio.id)
    assert isinstance(holdings, list)
    expected = {asset1.name: 30, asset2.name: 5}
    assert len(holdings) == 2
    for entry in holdings:
        assert 'asset_name' in entry and 'total_amount' in entry
        name = entry['asset_name']
        amount = entry['total_amount']
        assert name in expected and amount == expected[name]
