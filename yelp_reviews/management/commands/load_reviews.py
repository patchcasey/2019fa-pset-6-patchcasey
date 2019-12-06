from django.core.management import BaseCommand
from django.db import transaction
import dask.dataframe as dd
import pandas as pd
import os

from ...models import DimDate, FactReview

class Command(BaseCommand):
    help = "Load review facts"

    def add_arguments(self, parser):
        parser.add_argument("-f", "--full", action="store_true")

    def handle(self, *args, **options):

        #TODO - add way to pull data into pset data folder (for travis)
        # NOTE: - I chose to write the pset5 material directly in here because I did not get to that part of the pset5
        # before it was due - thus, it doesn't make sense to go back and append it there, just to pull into here
        # also - I chose to skip Luigi since I always have problems with it and stick to a basic but robust way of
        # importing the data by using a makefile and storing the data for the dask dataframe in data/

        data_path = os.path.abspath(os.path.join(os.getcwd(), "data"))
        reviews0 = dd.read_csv(os.path.join(data_path, "*.csv"),
                               parse_dates=['date'],
                               dtype={'cool': 'float64',
                                      'funny': 'float64',
                                      'stars': 'float64',
                                      'useful': 'float64'})
        reviews1 = reviews0.dropna(subset=["review_id", "user_id"])[reviews0["review_id"].str.len() == 22]
        reviews2 = reviews1.fillna(value={"funny": float(0), "cool": float(0), "useful": float(0), "stars": float(0)})
        reviews3 = reviews2.astype({"funny": "int64", "cool": "int64", "useful": "int64", "stars": "int64"})
        reviews = reviews3.map_partitions(lambda df: df.set_index("review_id"))
        reviews["count"] = 1

        dates_in_reviews = reviews.groupby("date")["count"].sum()
        df_dates = dates_in_reviews.compute()
        print(df_dates)

        analysis_in_reviews = (
            reviews.groupby("date")["stars", "useful", "funny", "cool", "count"]
                .sum()
                .astype({"stars": "int64",
                         "useful": "int64",
                         "funny": "int64",
                         "cool": "int64",
                         "count": "int64"})
                .reset_index()
                .set_index("date")
        )
        df_analysis = analysis_in_reviews.compute()
        print("df_analysis:\n",df_analysis)

        with transaction.atomic():
            date_objs = [
                DimDate(
                    date=idx
                )
                for idx, analysis in df_dates.iteritems()
            ]

            DimDate.objects.all().delete()
            DimDate.objects.bulk_create(date_objs)

        with transaction.atomic():
            review_objs = [
                FactReview(
                    date=DimDate.objects.get(date=idx),
                    count=analysis['count'],
                    stars=analysis['stars'],
                    useful=analysis['useful'],
                    funny=analysis['funny'],
                    cool=analysis['cool'],
                )
                for idx, analysis in df_analysis.iterrows()
            ]

            FactReview.objects.all().delete()
            FactReview.objects.bulk_create(review_objs)