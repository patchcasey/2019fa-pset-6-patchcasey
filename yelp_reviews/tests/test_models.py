from django.test import TestCase as DJTest
from unittest import TestCase

from yelp_reviews.models import DimDate, FactReview
from django.utils import timezone

# models test
class DimDateBasicTest(DJTest):
    def create_DimDate(self, date=timezone.now()):
        # set up a model object
        return DimDate.objects.create(date=date)

    def test_DimDate_creation(self):
        # make sure the data was added to model correctly
        w = self.create_DimDate()
        self.assertTrue(isinstance(w, DimDate))
        self.assertEqual(w.__str__(), w.date)


class FactReviewBasicTest(DJTest):
    def create_FactReview(
        self, date=timezone.now(), count=1, stars=1, useful=1, funny=1, cool=1
    ):
        # same as above but for FactReview model
        x = DimDate.objects.create(date=date)
        return FactReview.objects.create(
            date=x, count=count, stars=stars, useful=useful, funny=funny, cool=cool
        )

    def test_FactReview_creation(self):
        w = self.create_FactReview()
        self.assertTrue(isinstance(w, FactReview))
        self.assertEqual(w.__str__(), w.count)
