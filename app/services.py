from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point

from app.models import Asset, Institution, Portfolio, Transaction, User

UserModel = get_user_model()


class UserService:
    @staticmethod
    def create_user(username, password, role=User.ROLE_INVESTOR):
        return UserModel.objects.create_user(username=username, password=password, role=role)

    @staticmethod
    def get_by_username(username):
        return UserModel.objects.get(username=username)


class InstitutionService:
    @staticmethod
    def create_institution(name, type, location: Point):
        return Institution.objects.create(name=name, type=type, location=location)

    @staticmethod
    def get(pk):
        return Institution.objects.get(pk=pk)


class PortfolioService:
    @staticmethod
    def create_portfolio(user: User, name: str):
        return Portfolio.objects.create(user=user, name=name)

    @staticmethod
    def get(pk):
        return Portfolio.objects.get(pk=pk)

    @staticmethod
    def delete(pk):
        Portfolio.objects.filter(pk=pk).delete()


class AssetService:
    @staticmethod
    def create_asset(name, asset_type, institution: Institution):
        return Asset.objects.create(name=name, asset_type=asset_type, institution=institution)

    @staticmethod
    def get(pk):
        return Asset.objects.get(pk=pk)


class TransactionService:
    @staticmethod
    def create_transaction(portfolio: Portfolio, asset: Asset, trans_type: str, amount, price, date, details=None):
        return Transaction.objects.create(
            portfolio=portfolio,
            asset=asset,
            trans_type=trans_type,
            amount=amount,
            price=price,
            date=date,
            details=details,
        )

    @staticmethod
    def get(pk):
        return Transaction.objects.get(pk=pk)
