from rest_framework.viewsets import ModelViewSet, ViewSet
from django.shortcuts import render
from django.db.models import Sum

from .models import DimDate, FactReview
from .serializers import ByYearSerializer, DateSerializer, FactSerializer


class DateViewSet(ModelViewSet):
    serializer_class = DateSerializer
    queryset = DimDate.objects.all()

class FactViewSet(ModelViewSet):
    serializer_class = FactSerializer
    queryset = FactReview.objects.all()


class ByYear(ModelViewSet):
    serializer_class = ByYearSerializer

    def get_queryset(self):
        base = FactReview.objects.all()
        out_queryset = base.annotate(total_count=Sum('count')).values('total_count')
        return out_queryset

def render_aggregation(request):
    return render(request, "yelp_reviews/index.html", {})
