from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers

from .models import DimDate, FactReview


class FactSerializer(ModelSerializer):
    class Meta:
        model = FactReview
        fields = ["cool", "funny", "stars", "useful", "count"]


class DateSerializer(ModelSerializer):
    class Meta:
        model = DimDate
        fields = ["date"]


class ByYearSerializer(Serializer):
    year = serializers.IntegerField(default=0)
    total_count = serializers.IntegerField(default=0)
    avg_star = serializers.FloatField(default=0)
    cool = serializers.FloatField(default=0)
    avg_funny = serializers.FloatField(default=0)
    avg_useful = serializers.FloatField(default=0)
