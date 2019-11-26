from django.db import models


class DimDate(models.Model):
    date = models.DateField() # Date field


class FactReview(models.Model):
    date = models.ForeignKey(DimDate, on_delete=models.CASCADE) # ForeignKey
    count = models.IntegerField() # Integer field; number of reviews on that date
    stars = models.IntegerField() # Integer, sum of review.stars for all reviews on that date
    useful = models.IntegerField()
    funny = models.IntegerField()
    cool = models.IntegerField()
