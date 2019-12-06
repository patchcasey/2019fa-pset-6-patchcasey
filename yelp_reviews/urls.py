from django.urls import include, path
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view

from .views import ByYear, DateViewSet, FactViewSet, render_aggregation

router = DefaultRouter()

# Register some endpoints via "router.register(...)"
router.register(r"date", DateViewSet)
router.register(r"facts", FactViewSet)
router.register("by_year", ByYear, basename="by_year")

schema_view = get_schema_view(title="Yelp Review API")

urlpatterns = [
    path("api/", include(router.urls)),
    path("", render_aggregation, name="aggregation"),
]
