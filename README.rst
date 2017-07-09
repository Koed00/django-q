.. image:: docs/_static/logo.png
    :align: center
    :alt: Q logo
    :target: https://django-q.readthedocs.org/

A multiprocessing distributed task queue for Django
---------------------------------------------------

|image0| |image1| |docs| |image2|

Features
~~~~~~~~

-  Multiprocessing worker pool
-  Asynchronous tasks
-  Scheduled and repeated tasks
-  Encrypted and compressed packages
-  Failure and success database or cache
-  Result hooks, groups and chains
-  Django Admin integration
-  PaaS compatible with multiple instances
-  Multi cluster monitor
-  Redis, Disque, IronMQ, SQS, MongoDB or ORM
-  Rollbar support

Requirements
~~~~~~~~~~~~

-  `Django <https://www.djangoproject.com>`__ > = 1.8
-  `Django-picklefield <https://github.com/gintas/django-picklefield>`__
-  `Arrow <https://github.com/crsmithdev/arrow>`__
-  `Blessed <https://github.com/jquast/blessed>`__

Tested with: Python 2.7 & 3.6. Django 1.8.18, 1.10.7 and 1.11

Brokers
~~~~~~~
- `Redis <https://django-q.readthedocs.org/en/latest/brokers.html#redis>`__
- `Disque <https://django-q.readthedocs.org/en/latest/brokers.html#disque>`__
- `IronMQ <https://django-q.readthedocs.org/en/latest/brokers.html#ironmq>`__
- `Amazon SQS <https://django-q.readthedocs.org/en/latest/brokers.html#amazon-sqs>`__
- `MongoDB <https://django-q.readthedocs.org/en/latest/brokers.html#mongodb>`__
- `Django ORM <https://django-q.readthedocs.org/en/latest/brokers.html#django-orm>`__

Installation
~~~~~~~~~~~~

-  Install the latest version with pip::

    $ pip install django-q


-  Add `django_q` to your `INSTALLED_APPS` in your projects `settings.py`::

       INSTALLED_APPS = (
           # other apps
           'django_q',
       )

-  Run Django migrations to create the database tables::

    $ python manage.py migrate

-  Choose a message `broker <https://django-q.readthedocs.org/en/latest/brokers.html>`__ , configure and install the appropriate client library.

Read the full documentation at `https://django-q.readthedocs.org <https://django-q.readthedocs.org>`__


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
            'db': 0, }
    }

For full configuration options, see the `configuration documentation <https://django-q.readthedocs.org/en/latest/configure.html>`__.

Management Commands
~~~~~~~~~~~~~~~~~~~

Start a cluster with::

    $ python manage.py qcluster

Monitor your clusters with::

    $ python manage.py qmonitor

Check overall statistics with::

    $ python manage.py qinfo

Creating Tasks
~~~~~~~~~~~~~~

Use `async` from your code to quickly offload tasks:

.. code:: python

    from django_q.tasks import async, result

    # create the task
    async('math.copysign', 2, -2)

    # or with a reference
    import math.copysign

    task_id = async(copysign, 2, -2)

    # get the result
    task_result = result(task_id)

    # result returns None if the task has not been executed yet
    # you can wait for it
    task_result = result(task_id, 200)

    # but in most cases you will want to use a hook:

    async('math.modf', 2.5, hook='hooks.print_result')

    # hooks.py
    def print_result(task):
        print(task.result)

For more info see `Tasks <https://django-q.readthedocs.org/en/latest/tasks.html>`__


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
    import arrow

    schedule('math.hypot',
             3, 4,
             schedule_type=Schedule.MINUTES,
             minutes=5,
             repeats=24,
             next_run=arrow.utcnow().replace(hour=18, minute=0))

For more info check the `Schedules <https://django-q.readthedocs.org/en/latest/schedules.html>`__ documentation.


Testing
~~~~~~~

To run the tests you will need `py.test <http://pytest.org/latest/>`__ and `pytest-django <https://github.com/pytest-dev/pytest-django>`__


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

.. |image0| image:: https://travis-ci.org/Koed00/django-q.svg?branch=master
   :target: https://travis-ci.org/Koed00/django-q
.. |image1| image:: http://codecov.io/github/Koed00/django-q/coverage.svg?branch=master
   :target: http://codecov.io/github/Koed00/django-q?branch=master
.. |image2| image:: http://badges.gitter.im/Join%20Chat.svg
   :target: https://gitter.im/Koed00/django-q
.. |docs| image:: https://readthedocs.org/projects/docs/badge/?version=latest
    :alt: Documentation Status
    :scale: 100
    :target: https://django-q.readthedocs.org/
