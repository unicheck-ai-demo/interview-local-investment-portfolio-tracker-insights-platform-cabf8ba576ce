from django.contrib.gis.geos import Point
from rest_framework import serializers

from app.models import Asset, Institution, Portfolio, Transaction, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role']


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = ['id', 'name', 'type', 'location']

    def create(self, validated_data):
        location = validated_data.get('location')
        if isinstance(location, dict):
            coords = location.get('coordinates')
            validated_data['location'] = Point(coords[0], coords[1])
        return super().create(validated_data)


class PortfolioSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Portfolio
        fields = ['id', 'user', 'name', 'created_at']


class AssetSerializer(serializers.ModelSerializer):
    institution = InstitutionSerializer(read_only=True)

    class Meta:
        model = Asset
        fields = ['id', 'name', 'asset_type', 'institution']


class TransactionSerializer(serializers.ModelSerializer):
    portfolio = PortfolioSerializer(read_only=True)
    asset = AssetSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'portfolio', 'asset', 'trans_type', 'amount', 'price', 'date', 'details']
