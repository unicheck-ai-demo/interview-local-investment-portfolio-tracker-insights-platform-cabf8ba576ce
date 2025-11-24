import pytest
from django.contrib.gis.geos import Point

from app.models import Institution
from app.services import InstitutionService


@pytest.mark.django_db
@pytest.mark.xfail(strict=True)
def test_nearest_institutions_radius_km():
    origin = Institution.objects.create(name='Origin Bank', type=Institution.TYPE_BANK, location=Point(0, 0, srid=4326))
    loc2 = Point(0.018, 0, srid=4326)  # approximately 2 km east
    far = Institution.objects.create(name='Far Bank', type=Institution.TYPE_BANK, location=loc2)
    insts = list(InstitutionService.get_nearby(lat=0, lon=0, radius_km=3))
    assert origin in insts
    assert far in insts
    assert len(insts) == 2
