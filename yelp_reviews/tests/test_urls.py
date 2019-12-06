from django.conf import settings
from django.urls import reverse, resolve
from django.test import TestCase as DJTest
from ..views import ByYear, DateViewSet, FactViewSet, render_aggregation

class UrlTests(DJTest):

    def test_view_url_exists_at_desired_location(self):
        for x in ['date','facts','by_year']:
            response = self.client.get("/yelp/api/{}/".format(x))
            self.assertEqual(response.status_code, 200)

    def test_base_url(self):
        response2 = self.client.get("/")
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(resolve("/").url_name, "home")

    def test_byyear_url_name_correct(self):
        match = resolve("/yelp/api/by_year/")
        self.assertEqual(match.url_name, "by_year-list")
