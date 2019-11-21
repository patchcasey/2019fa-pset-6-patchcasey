# Pset 6

## Objective

In this homework we ask you to install and configure a Django application, load
provided data and perform some analysis via an API.  Your new API will be
self-documenting using built-in tooling.

NB: this pset utilizes CoreAPI, which is deprecated in favor of OpenAPI/Swagger.
Any real application of these ideas should use OpenAPI instead.  However,
because client code generation is simpler using CoreAPI, the pset has been left
in its original form for now.

You may note some deprecation errors and will either have to work with an older
version of Django REST Framework or solve those issues.  See eg
[DRF-6809](https://github.com/encode/django-rest-framework/issues/6809).

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Initial setup](#initial-setup)
  - [Data directory](#data-directory)
  - [`cookiecutter-django`](#cookiecutter-django)
  - [Pipenv](#pipenv)
  - [Docker](#docker)
  - [Django Setup](#django-setup)
    - [Database](#database)
      - [Option 1: sqlite](#option-1-sqlite)
      - [Option 2: postgres or your own](#option-2-postgres-or-your-own)
      - [Migrate!](#migrate)
    - [Running](#running)
    - [Debugging](#debugging)
    - [Testing](#testing)
- [Problems](#problems)
  - [Yelp Reviews](#yelp-reviews)
    - [Append to INSTALLED_APPS](#append-to-installed_apps)
  - [Creating Models](#creating-models)
    - [The DataMart](#the-datamart)
    - [Ensuring a Star Schema](#ensuring-a-star-schema)
    - [Migrating changes to the model](#migrating-changes-to-the-model)
    - [Admin Pages](#admin-pages)
  - [Loading Data](#loading-data)
      - [Reusing Pset 5](#reusing-pset-5)
    - [Travis Answers](#travis-answers)
  - [The API](#the-api)
    - [The Basics](#the-basics)
      - [Serializers](#serializers)
      - [Views](#views)
      - [URLs](#urls)
    - [Analytics](#analytics)
      - [Visualize it!](#visualize-it)
- [Optional: expanding dimensions](#optional-expanding-dimensions)
  - [Live Migrations](#live-migrations)
  - [New viewset and plot](#new-viewset-and-plot)
- [Resources](#resources)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Initial setup

Start by rendering a new app via your cookiecutter template and linking to this
repo as before.  Your app should be called 'Pset 6'

### Data directory

In the past, dask/luigi have automatically created a local data folder for us.
For simplicity, we'll do it manually this time:

```bash
# In repo:
mkdir data

# Force add a .gitkeep file
touch data/.gitkeep
git add -f data/.gitkeep
git commit -m "gitkeep data"
```

The last lines ensure that git will create the data directory when you clone the
project on travis, despite ignoring all the files inside it (your `.gitignore`
includes `/data/`, right?).  For reference, see [stack
overflow](https://stackoverflow.com/questions/7229885/what-are-the-differences-between-gitignore-and-gitkeep)

### `cookiecutter-django`

Our cookiecutter repo is not built for Django applications. There actually is a
fantastic repo
[cookiecutter-django](https://github.com/pydanny/cookiecutter-django) we will
consult and use as a supplement.

Use the following settings when you render the django template:

| setting | value |
| - | - |
| Project name | `Pset 6` |
| timezone | `UTC` |
| use_docker | `y` |
| use_travisci | `y` |
| debug | `y` |

```bash
cookiecutter gh:pydanny/cookiecutter-django
```

We will ***NOT*** commit or use this django project directly.  You can play
around with it and use it for reference.  Below, you will extract certain parts
into your main pset repo.

### Pipenv

You will likely need the following in your pset 6 to get started:

```bash
pipenv install django django-environ djangorestframework django-model-utils argon2-cffi django-allauth django-crispy-forms django-extensions coreapi
pipenv install --dev pytest-django django-debug-toolbar pytest-cov factory-boy
```

You can see all the requirements from the django template, but we want to
refactor them into a Pipfile for better isolation of dev/deploy packages.

Packages of note:

* [Pytest Django](https://pytest-django.readthedocs.io/en/latest/) will let us
use pytest instead of Django's default test runner

* [Django Environ](https://django-environ.readthedocs.io/en/latest/) will be
good for configuring django's settings via env variables

* [Django Debug Toolbar](https://django-debug-toolbar.readthedocs.io/en/latest/)

* [Django Extensions](https://django-extensions.readthedocs.io/en/latest/)

### Docker

If using docker, you'll need to expose the Django port to your local host.

Add this to the end of your `Dockerfile`:

```docker
EXPOSE 8000
```

And update `docker-compose.yml` as well:

```yaml
version: '3'
services:
  app:
    environment:
      - AWS_ACCESS_KEY_ID
      - AWS_SECRET_ACCESS_KEY
      - CSCI_SALT
    build:
      context: .
      args:
        - CI_USER_TOKEN=${CI_USER_TOKEN}

    volumes:
      - .:/app
    command: python manage.py runserver 0.0.0.0:8000
    ports:
      - "8000:8000"
```

Note that for running the webserver, you will need to run `docker-compose up`
rather than `./drun_app python manage.py runserver`.  You can use `./drun_app`
for migrations and management commands just fine.

### Django Setup

Rather than starting a django app from scratch, copy the `manage.py` from
the django template to the top level of your repo.

***Comment out*** the two lines in the `manage.py` file adding `pset_6` to the
path.  Our package structure will handle that better.

Also copy:

* the entire `config` package
* All the submodules and subpackages from cookiecutter's package `pset_6` into
the same places under your `pset_6`

Add `DJANGO_SETTINGS_MODULE=config.settings.test` your pytest config ini

Add `USE_DOCKER=yes` or `no` to your `.env` and Travis ('yes' if you're using
docker locally, always no on travis).  The django template helps us with some
configs (eg I couldn't get the debug toolbar to work in docker without that).

Running `pytest` should now work! Ensure it is picking up tests in the `pset_6`
package, specifically `users`, eg:

```bash
$ pytest
========================= test session starts =============================
platform darwin -- Python 3.7.3, pytest-4.4.1, py-1.8.0, pluggy-0.9.0
Django settings: config.settings.test (from ini file)
rootdir: 2019sp-pset-6-gorlins, inifile: setup.cfg, testpaths: tests, pset_6
plugins: django-3.4.8, cov-2.6.1
collected 10 items

tests/test_pset_6.py .                                               [ 10%]
pset_6/users/tests/test_forms.py .                                   [ 20%]
pset_6/users/tests/test_models.py .                                  [ 30%]
pset_6/users/tests/test_urls.py ....                                 [ 70%]
pset_6/users/tests/test_views.py ...                                 [100%]

---------- coverage: platform darwin, python 3.7.3-final-0 -----------
Name                                Stmts   Miss Branch BrPart     Cover   Missing
----------------------------------------------------------------------------------
pset_6/__init__.py                      1      0      0      0   100.00%
pset_6/__main__.py                      3      1      2      1    60.00%   14, 13->14
pset_6/cli.py                           6      0      0      0   100.00%
pset_6/conftest.py                     12      0      0      0   100.00%
pset_6/contrib/__init__.py              0      0      0      0   100.00%
pset_6/contrib/sites/__init__.py        0      0      0      0   100.00%
pset_6/users/__init__.py                0      0      0      0   100.00%
pset_6/users/adapters.py               11      2      0      0    81.82%   11, 16
pset_6/users/admin.py                  12      0      2      0   100.00%
pset_6/users/apps.py                    9      0      0      0   100.00%
pset_6/users/forms.py                  18      0      0      0   100.00%
pset_6/users/models.py                  8      0      0      0   100.00%
pset_6/users/tests/__init__.py          0      0      0      0   100.00%
pset_6/users/tests/factories.py        14      0      0      0   100.00%
pset_6/users/tests/test_forms.py       15      0      0      0   100.00%
pset_6/users/tests/test_models.py       5      0      0      0   100.00%
pset_6/users/tests/test_urls.py        16      0      0      0   100.00%
pset_6/users/tests/test_views.py       25      0      0      0   100.00%
pset_6/users/urls.py                    4      0      0      0   100.00%
pset_6/users/views.py                  28      0      0      0   100.00%
----------------------------------------------------------------------------------
TOTAL                                 187      3      4      1    97.91%

========================= 10 passed in 1.00 seconds =========================
```

#### Database

##### Option 1: sqlite

For simplicity, we can get away with a local sqlite DB.  If you run `python
manage.py runserver` you will notice that it complains about a missing env var.
Set that in your `.env` and travis as:

```bash
DATABASE_URL=sqlite:///data/db.sqlite
```

##### Option 2: postgres or your own

If you'd like, you can set up a full postgres database (or any other) for your
local development.  The docs for cookiecutter-django walk through how to set
that up; additionally, they will create a postgres db using docker containers
which you can use if you'd like (if using docker).

##### Migrate!

Before we do anything, we will need to run the `migrate` command, which will
mostly migrate built-in Django user authentication tables.

```bash
python manage.py migrate
python manage.py createsuperuser # user:pass = admin:admin if you'd like
```

#### Running

Run the test server via:

```bash
python manage.py runserver
# or
docker-compose up
```

Open up [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in a browser, and poke
around!  Also check out the admin panel
([http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)) and ensure
everything looks good!

#### Debugging

You can't simply start a debugger with django, as it requires some setup.  Here
are a few tips:

* `python manage.py shell` will start an interactive console

* You can set up a scratch file and manually [set up
django](https://docs.djangoproject.com/en/2.2/topics/settings/#calling-django-setup-is-required-for-standalone-django-usage),
just ensure `DJANGO_SETTINGS_MODULE` is in your env (see `manage.py` to set that
automatically)

* To kick off a management command in a scratch file, after setting up django,
use
[call_command](https://docs.djangoproject.com/en/2.2/ref/django-admin/#django.core.management.call_command)

* For debugging the webservice itself, debug toolbar helps a lot.  There is also
the Werkzeug debugger you can invoke with
[runserver_plus](https://django-extensions.readthedocs.io/en/latest/runserver_plus.html).
Pycharm Pro will also let you start a django webservice directly and set
breakpoints!

#### Testing

Write tests against endpoints using [DRF
Testing](https://www.django-rest-framework.org/api-guide/testing/).

For Django tests, use Django's TestCase subclass (`django.test.TestCase`) when
you need to test against a database.  See [testing
docs](https://docs.djangoproject.com/en/2.2/topics/testing/).  Use vanilla
`TestCase`'s if you don't need the DB or a live server.

```python
# This is confusing, avoid:
from django.test import TestCase

# Rather,
from django.test import TestCase as DJTest
from unittest import TestCase
```

## Problems

### Yelp Reviews

Inside the project (in the same directory where you'll find the `manage.py`),
create a new app called `yelp_reviews` as follows:

```bash
python manage.py startapp yelp_reviews
```

Be sure to add the package to your test paths and `--cov=yelp_reviews` in your
pytest config.

Keeping this as a separate package (rather than `pset_6.yelp_reviews`) helps us
build a modular Django site, where `yelp_reviews` could be added to another site
in the future.

#### Append to INSTALLED_APPS

In order to use the django rest framework (DRF) we need to add it to our
installed apps in `config.settings.base`. We also need to add our new
`yelp_reviews` app!

Ensure the following are in your `INSTALLED_APPS` list (it looks different in
the cookiecutter-django structure):

```python
INSTALLED_APPS = [
  ...
  'rest_framework',
  'yelp_reviews.apps.YelpReviewsConfig',
]
```

### Creating Models

This assignment is accompanied by the Yelp dataset that you worked with for Pset
5.

#### The DataMart

Create models adhering to the database design pricinples of a
[star-schema](https://www.vertabelo.com/blog/technical-articles/data-warehouse-modeling-star-schema-vs-snowflake-schema).

For this particular dataset, design 2 models that will allow us to calculate
statistics about the average facts by date.  Because this is a "Fact" table, we
want all the facts to be ***summary statistics***, ie the sum of all properties
within that group.

In `yelp_reviews.models`:

```python
from django.db.models import ...


class DimDate(models.Model):
    date = ... # Date field


class FactReview(Model):
    date = ... # ForeignKey
    count = ... # Integer field; number of reviews on that date
    stars = ... # Integer, sum of review.stars for all reviews on that date
    useful = ...
    funny = ...
    cool = ...
```

(Note that we are dropping many of the fields from our original csv - text,
user_id, business_id, etc.  The grouping we want above is date, so there should
only be one row for any given date, not one row per review).

See
[here](https://docs.djangoproject.com/en/2.2/ref/models/fields/#django.db.models.ForeignKey.on_delete)
for setting `on_delete` for the ForeignKey.

Note you may want to apply unique constraints on both models.  For FactReview,
you may get a warning about using a `OneToOneField` if you use unique; you can
ignore or achieve the same thing using `unique_together` as a model option since
that will be slightly better if we ever add another dimension to the fact table.


#### Ensuring a Star Schema

The above exemplifies a Star Schema.  You could instead start with a simpler
approach (which will be much easier for loading the data), but you will not
receive full credit.  The simpler approach only uses `FactReview` with a
`DateField` instead of a `ForeignKey` to `DimDate`.

If you do merge to master with a simple `DateField`, when you come back to
upgrade to a proper dimension, you should ensure you have a live migration plan
(see the optional section below for an example).

#### Migrating changes to the model

When you believe your models are working as designed you must create migrations
and apply them before they can be used!

```bash
python manage.py makemigrations
python manage.py migrate
```

If your migration is successful, you should commit the migration file to the
repo.  You can also migrate backwards (sometimes) and modify the migration files
as necessary; however, once a migration file is merged to master, it should be
considered 'in production' and never modified (you can always add a new
migration file that undoes a previous one).

#### Admin Pages

You should create admin models so you can view this in the admin UI!

Tips regarding some funny Django Admin behaviors:

* The display of the model in the list page is defined by `__str__(self)`
* If you get an error like `The value of 'list_display[0]' refers to '...', which is not a callable` when you want to display an object property, you can use
`lamba obj: obj.field` where you would normally have provided the field name
* The admin page can get slow when viewing ForeignKey items.  If you make them
readonly in the admin, it helps a lot!

See [admin options](https://docs.djangoproject.com/en/2.2/ref/contrib/admin/#modeladmin-options)

### Loading Data

Create a [management
command](https://docs.djangoproject.com/en/2.2/howto/custom-management-commands/)
called `load_reviews` under `yelp_reviews`.  It will load the review data.

It will look something like this:

```python
from django.core.management import BaseCommand

from ...models import DimDate, FactReview


class Command(BaseCommand):
    help = "Load review facts"

    def add_arguments(self, parser):
        parser.add_argument("-f", "--full", action="store_true")

    def handle(self, *args, **options):
        ... # Logic goes here
```


The `--full` argument should be `False` by default and serve the same purpose
as it did in pset 5 (only load the first partition if `not full`)

Hints:

* Feel free to use luigi, dask, pandas, etc (just pipenv install them).
* You should probably use dask for calculating the initial stats initially
* Feel free to use an atomic Luigi target, or not
* You may want a way to flush the DB (eg `FactReview.objects.all().delete()`)
* For a star schema, you must create the dimensions first
* Your load should be atomic, but you don't need luigi necessarily
* Use django batteries copiously.  These may help:
  * You could try to build off [loadddata](https://docs.djangoproject.com/en/2.2/ref/django-admin/#loaddata) (or not)
  * [transactions.atomic](https://docs.djangoproject.com/en/2.2/topics/db/transactions/#django.db.transaction.atomic)
  * [queryset.bulk_create](https://docs.djangoproject.com/en/2.1/ref/models/querysets/#bulk-create)
  * [queryset.in_bulk](https://docs.djangoproject.com/en/2.1/ref/models/querysets/#in-bulk)

Call it with:

```bash
python manage.py load_reviews
```

(or `call_command` as noted above if developing with a scratch file).

Check that you can see the results in the DB once you've loaded them.

##### Reusing Pset 5

Since this application depends on the same preprocessing as Pset 5, we want to
share code!  However, Pset 5 is not designed as a library.  Short of
copy/pasting the code into your new repo, you have a few options how to best
leverage your existing work:

* Add a setup.py to pset 5 and pip install it, much like `csci_utils`!
* Add (some) code to `csci_utils`.  However, we want to keep this library fairly
generic, so it might not be best to copy an entire pset there
* Hard-code some of the data output paths (creating data dependencies between
the psets)
* Literally pull the code into your repo with a git subtree or git submodule

Justify your decisions in comments where you pull in the data to pset 6!

#### Travis Answers

Update your `.travis.yml` `answers` build:

```yaml
- stage: answers
  script:
    - python manage.py migrate
    - python manage.py load_reviews
    - python manage.py summarize
```

And add a `summarize` management command:

```python
from django.core.management import BaseCommand
from django.db.models import Sum

from ...models import DimDate, FactReview


class Command(BaseCommand):
    help = "Summarize review facts"

    def handle(self, *args, **options):
        print("Dimensions: {}".format(DimDate.objects.all().count()))
        print("Facts: {}".format(FactReview.objects.all().count()))
        print("Total Reviews: {}".format(FactReview.objects.aggregate(Sum("count"))))
```

You should see something like:

```bash
$ python manage.py summarize
Dimensions: XX
Facts: XX
Total Reviews: {'count__sum': XX}
```

### The API

#### The Basics

##### Serializers

Create a new file `serializers.py` in the `yelp_reviews` package.

```python
from rest_framework.serializers import ModelSerializer

from .models import DimDate, FactReview

class FactSerializer(ModelSerializer):
    class Meta:
        ...

class DateSerializer(ModelSerializer):
    ...
```

##### Views

In `yelp_reviews.views`:

```python
from rest_framework.viewsets import ModelViewSet, ViewSet

from .models import DimDate, FactReview
from .serializers import ByYearSerializer, DateSerializer, FactSerializer


class DateViewSet(ModelViewSet):
    ...

class FactViewSet(ModelViewSet):
    ...
```

##### URLs

Create a new file `urls.py` in the `yelp_reviews` directory.

```python
from django.urls import include, path
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view

from .views import ByYear, DateViewSet, FactViewSet, render_aggregation

router = DefaultRouter()

# Register some endpoints via "router.register(...)"
router.register(...)

schema_view = get_schema_view(title="Yelp Review API")

urlpatterns = [
    path("api/", include(router.urls)),
]
```

And finally, in `config.urls` file:

```python
urlpatterns = [
    ...
    # Your stuff: custom urls includes go here
    path(
        "yelp/",
        include(("yelp_reviews.urls", "yelp_reviews"), namespace="yelp_reviews"),
    ),
    path("docs/", include_docs_urls(title="Pset 6 API")),
]
```

You should now be able to browse your api via the CoreAPI UI
[/docs/](http://localhost:8000/docs/) as well as the direct
[/yelp/api](http://localhost:8000/yelp/api/)!

If you'd like, add this to `config.settings.base` to speed up browsing:

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10
}
```

#### Analytics

Let's add some power to our API!

```python
# yelp_reviews.serializer
class ByYearSerializer(Serializer):
    # Return the *averages*, not the sum!
    ...

# yelp_reviews.views
class ByYear(ModelViewSet):

    def get_queryset(self):
        base = FactReview.objects.all()

        # Group by year, sum all facts, calculate mean using the count
        # Note this MUST be done on the DB side, not in pandas or dask!
        ...

        return out_queryset

# yelp_reviews.urls
router.register("by_year", ByYear, basename="by_year")
```

For the `ByYear` viewset and serializer, you want to calculate the ***average***
fact per review (stars, funny, etc) using the summary stats you've collected.

This must happen on the DB side, and only return 1 row per year.

Hints:

* From `django.db.models`, use
[aggregations](https://docs.djangoproject.com/en/2.2/topics/db/aggregation/)
like `Sum` and [field
lookups](https://docs.djangoproject.com/en/2.2/ref/models/expressions/#django.db.models.F)
like `F`
* You can find DB side functions in `django.db.models.functions` to eg extract
parts of a date object

##### Visualize it!

We'll use Vega, a light-weight JS library, to plot our data.  Add the following:

```python
# yelp_reviews.views
def render_aggregation(request):
    return render(request, "yelp_reviews/index.html", {})

# yelp_reviews.urls
urlpatterns = [
    ...
    path("", render_aggregation, name="aggregation"),
]
```

Now add this template to `yelp_reviews/templates/yelp_reviews/index.html`:

```html
{% extends "base.html" %}

{% block content %}
<!--
    Load the CoreAPI library and the API schema.

    /static/rest_framework/js/coreapi-0.1.1.js
    /docs/schema.js
-->
{% load static %}
<script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-lite@3"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-embed@3"></script>
<script src="{% static 'rest_framework/js/coreapi-0.1.1.js' %}"></script>
<script src="{% url 'api-docs:schema-js' %}"></script>
<script type="text/javascript">
const coreapi = window.coreapi
const schema = window.schema
var client = new coreapi.Client()

client.action(schema, ["by_year", "list"]).then(function(result) {
    // Return value is in 'result'
    vegaEmbed('#vis', {
      "$schema": "https://vega.github.io/schema/vega-lite/v3.json",
      "description": "Average stats per year",
      "width": 500, "height": 250,
      "data": {
         "values": result.results,
      },
      "mark": {
        "type": "line"
      },
      "encoding": {
        "x": {"field": "year", "type": "quantitative", "axis":{"format": "d"}},
        "y": {"field": "cool", "type": "quantitative"}
      }
    });
})

</script>
<h3>Aggregation</h3>
<div id="vis"></div>
{% endblock %}
```

For ease of navigation, add this snippet to `base.html` in `pset_6/templates`:

```html
...
<ul class="navbar-nav mr-auto">
  <li class="nav-item active">
    <a class="nav-link" href="{% url 'home' %}">Home <span class="sr-only">(current)</span></a>
  </li>

  <!-- Add this bit here -->
  <li class="nav-item">
    <a class="nav-link" href="{% url 'yelp_reviews:aggregation' %}">Yelp</a>
  </li>
  ...
</ul>
```

You'll now see a link to our aggregation on the homepage.  Take a look!

You should download this image (after loading the ***full*** dataset) to
upload in your answers quiz.

## Optional: expanding dimensions

We can accomplish a number of aggregations using SQL functions on a date, but
we can't do everything.

Let's add a new aggregation by whether the review was on a holiday.

You can use any function you'd like to determine whether a date is a holiday.
This library looks easy: [holidays](https://pypi.org/project/holidays/).

### Live Migrations

Add a field `is_holiday` to `DimDate`.  Note - we cannot simply add and migrate
it, since you presumably have data already!

Create a 'live migration' using the following pattern:

1. Create the field while allowing nulls.  Ensure all code that writes to
`DimDate` is populating the field, but there is no default value.  Commit the
code.
2. Deploy code (if this were not a pset!) and migrate all DB's.
3. Write a data migration which updates all null values.  Ensure it uses the
same logic used to write to `DimDate`.  Run the migration.
4. Create a final migration which makes the field non-nullable, and migrate.

### New viewset and plot

After we know `is_holiday` is guaranteed to be populated, create a new
aggregation view set and plot as above.  Ensure the aggregation groups over
`date__is_holiday` and does not calculate the holiday logic itself!

## Resources

- [Django Documentation](https://docs.djangoproject.com/en/2.2/)
- [Django Rest Framework](https://www.django-rest-framework.org/)
