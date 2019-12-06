from django.test import TestCase as DJTest
from unittest import TestCase

from yelp_reviews.serializers import FactSerializer, DateSerializer, ByYearSerializer
from yelp_reviews.models import FactReview, DimDate
from django.utils import timezone


class SerializerTests(DJTest):
    # adapted from https://www.vinta.com.br/blog/2017/how-i-test-my-drf-serializers/
    def setUp(self):
        # create instances of models/serializers to be tested
        self.create_DimDate = {"date": "2019-01-01"}

        self.case_DimDate = DimDate.objects.create(**self.create_DimDate)
        self.case_date_serializer = DateSerializer(instance=self.case_DimDate)

        self.create_FactReview = {
            "date": self.case_DimDate,
            "cool": 1,
            "funny": 1,
            "stars": 1,
            "useful": 1,
            "count": 1,
        }

        self.case_FactReview = FactReview.objects.create(**self.create_FactReview)
        self.case_fact_serializer = FactSerializer(instance=self.case_FactReview)

    def test_contains_expected_fields(self):
        # ensures date and fact model serializer pulls out correct keys
        date_data = self.case_date_serializer.data
        self.assertEqual(list(date_data.keys()), ["date"])

        fact_data = self.case_fact_serializer.data
        self.assertEqual(
            list(fact_data.keys()), ["cool", "funny", "stars", "useful", "count"]
        )

    def test_serializer_content(self):
        # ensures date and fact model serializers have correct data for each key
        date_data = self.case_date_serializer.data
        fact_data = self.case_fact_serializer.data

        self.assertEqual(date_data["date"], self.create_DimDate["date"])

        fact_list = ["cool", "funny", "stars", "useful", "count"]
        for x in fact_list:
            self.assertEqual(fact_data[x], self.create_FactReview[x])

    def test_serializer_accepts_correctformats(self):
        # ensures if there is an incorrectly formatted input, an error is raised
        self.create_DimDate["date"] = 102938
        bad_date_serializer = DateSerializer(data=self.create_DimDate)

        self.assertFalse(bad_date_serializer.is_valid())
        self.assertEqual(set(bad_date_serializer.errors), set(["date"]))

        self.create_FactReview["cool"] = "string"
        bad_fact_serializer = FactSerializer(data=self.create_FactReview)

        self.assertFalse((bad_fact_serializer.is_valid()))
        self.assertEqual(set(bad_fact_serializer.errors), set(["cool"]))

    def test_fields_ByYearSerializer(self):
        # tests the ByYear serializer to ensure it has correct keys for data
        self.case_byyear_serializer = ByYearSerializer(instance=self.case_FactReview)
        byyear_data = self.case_byyear_serializer.data
        self.assertEqual(
            list(byyear_data.keys()),
            ["year", "total_count", "avg_star", "cool", "avg_funny", "avg_useful"],
        )

    def test_fieldformats_ByYearSerializer(self):
        # ensures the ByYear serializer fields are of correct format (important for the aggregations)
        self.case_byyear_serializer = ByYearSerializer(instance=self.case_FactReview)
        byyear_data = self.case_byyear_serializer.data
        self.assertEqual(type(byyear_data["cool"]), float)
        self.assertEqual(type(byyear_data["total_count"]), int)
        self.assertEqual(type(byyear_data["year"]), int)
