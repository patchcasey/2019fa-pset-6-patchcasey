from django.core.management import BaseCommand
from django.db import transaction
import dask.dataframe as dd
import os

# from ...models import DimDate, FactReview


def handle():
    # TODO - load dimdates into that model
    data_path = os.path.abspath(os.path.join(os.getcwd(), "..", "..", "..", "data"))
    reviews = dd.read_csv(data_path + "\*.csv",
                          parse_dates=['date'],
                          dtype={'cool':'float64',
                                  'funny':'float64',
                                  'stars':'float64',
                                  'useful':'float64'})
    numcols = ["funny", "cool", "useful", "stars"]
    reviews.dropna(subset=["review_id", "user_id"])
    [reviews["review_id"].str.len() == 22]
    reviews.fillna(value={"funny": float(0), "cool": float(0), "useful": float(0), "stars": float(0)})
    reviews.astype({"funny": "int64", "cool": "int64", "useful": "int64", "stars": "int64"})
    reviews.map_partitions(lambda df: df.set_index("review_id"))
    print(reviews)

class Command(BaseCommand):
    help = "Load review facts"

    def add_arguments(self, parser):
        parser.add_argument("-f", "--full", action="store_true")

    # def handle(self, *args, **options):
    #
    #     #TODO - load dimdates into that model
    #     data_path = os.path.abspath(os.path.join(os.getcwd(),"..","..","..","data"))
    #     print(data_path)
    #     reviews = dd.from_csv()

        #TODO - load factreview linking to this model (in line date=...)

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
                for idx, analysis in reviews_analysis.iterrows()
            ]

            FactReview.objects.all().delete()
            FactReview.objects.bulk_create(review_objs)

if __name__ == "__main__":
    handle()