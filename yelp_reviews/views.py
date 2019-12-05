from rest_framework.viewsets import ModelViewSet, ViewSet
from django.shortcuts import render
from django.db.models import Sum, F, FloatField, ExpressionWrapper
from django.db.models.functions import TruncYear, ExtractYear
from django.db.models.functions import Cast

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
        # query_date = base.annotate(year=TruncYear('date__date'))
        # out_queryset = query_date.annotate(total_count=Sum('count')).values('total_count')
        # return out_queryset

        # out_queryset = (
        #     base.annotate(year = ExtractYear('date__date')).values('year')
        #     .annotate(total_count=Sum(F('count')),
        #               avg_star=ExpressionWrapper(Sum(F('stars')) / Sum(F('count')), output_field=FloatField()),
        #               avg_cool=ExpressionWrapper(Sum(F('cool')) / Sum(F('count')), output_field=FloatField()),
        #               avg_funny=ExpressionWrapper(Sum(F('funny')) / Sum(F('count')), output_field=FloatField()),
        #               avg_useful=ExpressionWrapper(Sum(F('useful')) / Sum(F('count')), output_field=FloatField()))
        # )
        # return out_queryset

        # out_queryset = (
        #     base.annotate(year = ExtractYear('date__date')).values('year')
        #     .annotate(total_count=Sum(F('count')),
        #               avg_star=Cast(Sum(F('stars')) / Sum(F('count')), FloatField()),
        #               cool=Cast(Sum(F('cool')) / Sum(F('count')), FloatField()),
        #               avg_funny=Cast(Sum(F('funny')) / Sum(F('count')), FloatField()),
        #               avg_useful=Cast(Sum(F('useful')) / Sum(F('count')), FloatField()))
        # )
        # return out_queryset

        out_queryset = (
            base.annotate(year=ExtractYear('date__date')).values('year')
                .annotate(total_count=Sum(F('count')),
                          avg_star=Cast(Cast(Sum(F('stars')), FloatField()) / Cast(Sum(F('count')), FloatField()), FloatField()),
                          cool=Cast(Cast(Sum(F('cool')), FloatField()) / Cast(Sum(F('count')), FloatField()),
                                        FloatField()),
                          avg_funny=Cast(Cast(Sum(F('funny')), FloatField()) / Cast(Sum(F('count')), FloatField()),
                                        FloatField()),
                          avg_useful=Cast(Cast(Sum(F('useful')), FloatField()) / Cast(Sum(F('count')), FloatField()),
                                        FloatField()))
        )
        return out_queryset

def render_aggregation(request):
    return render(request, "yelp_reviews/index.html", {})
