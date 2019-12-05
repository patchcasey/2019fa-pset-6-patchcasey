from django.db import models


class DimDate(models.Model):
    date = models.DateField(unique=True) # Date field


class FactReview(models.Model):
    date = models.ForeignKey(DimDate, on_delete=models.CASCADE) # ForeignKey
    count = models.IntegerField(default=0) # Integer field; number of reviews on that date
    stars = models.IntegerField(default=0) # Integer, sum of review.stars for all reviews on that date
    useful = models.IntegerField(default=0)
    funny = models.IntegerField(default=0)
    cool = models.IntegerField(default=0)

    class Meta:
        unique_together = ('id', 'date')
