from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers

from .models import DimDate, FactReview

class FactSerializer(ModelSerializer):
    class Meta:
        model = FactReview
        fields = ['cool', 'funny', 'stars', 'useful', 'count']

class DateSerializer(ModelSerializer):
    class Meta:
        model = DimDate
        fields = ['date']

class ByYearSerializer(Serializer):
    total_count = serializers.IntegerField(default=0)