A multiprocessing distributed task queue for Django
---------------------------------------------------

|image0| |image1| |docs| |downloads|

Django Q2 is a fork of Django Q. Big thanks to Ilan Steemers for starting this project. Unfortunately, development has stalled since June 2021. Django Q2 is the new updated version of Django Q, with dependencies updates, docs updates and several bug fixes. Original repository: https://github.com/Koed00/django-q

Features
~~~~~~~~

-  Multiprocessing worker pool
-  Asynchronous tasks
-  Scheduled, cron and repeated tasks
-  Signed and compressed packages
-  Failure and success database or cache
-  Result hooks, groups and chains
-  Django Admin integration
-  PaaS compatible with multiple instances
-  Multi cluster monitor
-  Redis, IronMQ, SQS, MongoDB or ORM
-  Rollbar and Sentry support

Changes compared to the original Django-Q:

- Dropped support for Disque (hasn't been updated in a long time)
- Dropped Redis, Arrow and Blessed dependencies
- Updated all current dependencies
- Added tests for Django 4.x and 5.x
- Added Turkish language
- Improved admin area
- Fixed a lot of issues

See the `changelog <https://github.com/GDay/django-q2/blob/master/CHANGELOG.md>`__ for all changes.

Requirements
~~~~~~~~~~~~

-  `Django <https://www.djangoproject.com>`__ > = 3.2
-  `Django-picklefield <https://github.com/gintas/django-picklefield>`__

Tested with: Python 3.8, 3.9, 3.10, 3.11 and 3.12. Works with Django 3.2.X, 4.1.X, 4.2.X and 5.0.X

Brokers
~~~~~~~
- `Redis <https://django-q2.readthedocs.org/en/latest/brokers.html#redis>`__
- `IronMQ <https://django-q2.readthedocs.org/en/latest/brokers.html#ironmq>`__
- `Amazon SQS <https://django-q2.readthedocs.org/en/latest/brokers.html#amazon-sqs>`__
- `MongoDB <https://django-q2.readthedocs.org/en/latest/brokers.html#mongodb>`__
- `Django ORM <https://django-q2.readthedocs.org/en/latest/brokers.html#django-orm>`__

Installation
~~~~~~~~~~~~

-  Install the latest version with pip::

    $ pip install django-q2


-  Add `django_q` to your `INSTALLED_APPS` in your projects `settings.py`::

       INSTALLED_APPS = (
           # other apps
           'django_q',
       )

-  Run Django migrations to create the database tables::

    $ python manage.py migrate

-  Choose a message `broker <https://django-q2.readthedocs.org/en/latest/brokers.html>`__, configure and install the appropriate client library.

Read the full documentation at `https://django-q2.readthedocs.org <https://django-q2.readthedocs.org>`__

Configuration
~~~~~~~~~~~~~

All configuration settings are optional. e.g:

.. code:: python

    # settings.py example
    Q_CLUSTER = {
        'name': 'myproject',
        'workers': 8,
        'recycle': 500,
        'timeout': 60,
        'compress': True,
        'cpu_affinity': 1,
        'save_limit': 250,
        'queue_limit': 500,
        'label': 'Django Q',
        'redis': {
            'host': '127.0.0.1',
            'port': 6379,
            'db': 0,
        }
    }

For full configuration options, see the `configuration documentation <https://django-q2.readthedocs.org/en/latest/configure.html>`__.

Management Commands
~~~~~~~~~~~~~~~~~~~

For the management commands to work, you will need to install Blessed: <https://github.com/jquast/blessed>

Start a cluster with::

    $ python manage.py qcluster

Monitor your clusters with::

    $ python manage.py qmonitor

Monitor your clusters' memory usage with::

    $ python manage.py qmemory

Check overall statistics with::

    $ python manage.py qinfo

Creating Tasks
~~~~~~~~~~~~~~

Use `async_task` from your code to quickly offload tasks:

.. code:: python

    from django_q.tasks import async_task, result

    # create the task
    async_task('math.copysign', 2, -2)

    # or with a reference
    import math.copysign

    task_id = async_task(copysign, 2, -2)

    # get the result
    task_result = result(task_id)

    # result returns None if the task has not been executed yet
    # you can wait for it
    task_result = result(task_id, 200)

    # but in most cases you will want to use a hook:

    async_task('math.modf', 2.5, hook='hooks.print_result')

    # hooks.py
    def print_result(task):
        print(task.result)

For more info see `Tasks <https://django-q2.readthedocs.org/en/latest/tasks.html>`__

Schedule
~~~~~~~~

Schedules are regular Django models. You can manage them through the
Admin page or directly from your code:

.. code:: python

    # Use the schedule function
    from django_q.tasks import schedule

    schedule('math.copysign',
             2, -2,
             hook='hooks.print_result',
             schedule_type=Schedule.DAILY)

    # Or create the object directly
    from django_q.models import Schedule

    Schedule.objects.create(func='math.copysign',
                            hook='hooks.print_result',
                            args='2,-2',
                            schedule_type=Schedule.DAILY
                            )

    # Run a task every 5 minutes, starting at 6 today
    # for 2 hours
    from datetime import datetime

    schedule('math.hypot',
             3, 4,
             schedule_type=Schedule.MINUTES,
             minutes=5,
             repeats=24,
             next_run=datetime.utcnow().replace(hour=18, minute=0))

    # Use a cron expression
    schedule('math.hypot',
             3, 4,
             schedule_type=Schedule.CRON,
             cron = '0 22 * * 1-5')

For more info check the `Schedules <https://django-q2.readthedocs.org/en/latest/schedules.html>`__ documentation.

Testing
~~~~~~~

Running tests is easy with docker compose, it will also start the necessary databases. Just run:

.. code:: bash

    docker-compose -f test-services-docker-compose.yaml run --rm django-q2 poetry run pytest

Locale
~~~~~~

Currently available in English, German, Turkish, and French.
Translation pull requests are always welcome.

Todo
~~~~

-  Better tests and coverage
-  Less dependencies?

Acknowledgements
~~~~~~~~~~~~~~~~

-  Django Q was inspired by working with
   `Django-RQ <https://github.com/ui/django-rq>`__ and
   `RQ <https://github.com/ui/django-rq>`__
-  Human readable hashes by
   `HumanHash <https://github.com/zacharyvoase/humanhash>`__
-  Redditors feedback at `r/django <https://www.reddit.com/r/django/>`__

-  JetBrains for their `Open Source Support Program <https://www.jetbrains.com/community/opensource>`__

.. |image0| image:: https://github.com/GDay/django-q2/actions/workflows/test.yml/badge.svg?branche=master
   :target: https://github.com/GDay/django-q2/actions?query=workflow%3Atests
.. |image1| image:: https://coveralls.io/repos/github/GDay/django-q2/badge.svg?branch=master
   :target: https://coveralls.io/github/GDay/django-q2?branch=master
.. |docs| image:: https://readthedocs.org/projects/docs/badge/?version=latest
    :alt: Documentation Status
    :scale: 100
    :target: https://django-q2.readthedocs.org/
.. |downloads| image:: https://img.shields.io/pypi/dm/django-q2
   :target: https://img.shields.io/pypi/dm/django-q2
