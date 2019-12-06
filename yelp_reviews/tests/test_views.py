from django.conf import settings
from django.urls import reverse, resolve
from django.test import TestCase as DJTest
from rest_framework.test import APIRequestFactory

from ..views import DateViewSet, FactViewSet, ByYear, render_aggregation
from ..models import DimDate, FactReview


class UrlTests(DJTest):
    def setUp(self):
        # create instances necessary to test views
        self.create_DimDate = {"date": "2019-01-01"}

        self.case_DimDate = DimDate.objects.create(**self.create_DimDate)

        self.create_FactReview = {
            "date": self.case_DimDate,
            "cool": 1,
            "funny": 1,
            "stars": 1,
            "useful": 1,
            "count": 1,
        }
        self.case_FactReview = FactReview.objects.create(**self.create_FactReview)

    def test_DateViewSet(self):
        # queries the API to see if the view holds the correct data

        response = self.client.get("/yelp/api/date/")
        data = response.data["results"][0]
        self.assertEqual(data, {"date": "2019-01-01"})

    def test_FactViewSet(self):
        # queries the API to see if the view holds the correct data

        response = self.client.get("/yelp/api/facts/")
        data = response.data["results"][0]
        self.assertEqual(
            data, {"cool": 1, "funny": 1, "stars": 1, "useful": 1, "count": 1}
        )

    def test_ByYearView(self):
        # queries the API to see if the view holds the correct data

        response = self.client.get("/yelp/api/by_year/")
        data = dict(response.data["results"][0])["year"]
        self.assertEqual(data, 2019)

    def render_template(self):
        # ensures that rendering the template goes to the correct page, gives 200 code, and uses correct html template

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
