.. image:: docs/_static/logo.png
    :align: center
    :alt: Q logo
    :target: https://django-q.readthedocs.org/

A multiprocessing task queue for Django
---------------------------------------

|image0| |image1| |docs| |image2|

Features
~~~~~~~~

-  Multiprocessing worker pool
-  Asynchronous tasks
-  Scheduled and repeated tasks
-  Encrypted and compressed packages
-  Failure and success database
-  Result hooks
-  Django Admin integration
-  PaaS compatible with multiple instances
-  Multi cluster monitor
-  Redis
-  Python 2 and 3

Requirements
~~~~~~~~~~~~

-  `Redis-py <https://github.com/andymccurdy/redis-py>`__
-  `Django <https://www.djangoproject.com>`__ > = 1.7
-  `Django-picklefield <https://github.com/gintas/django-picklefield>`__
-  `Arrow <https://github.com/crsmithdev/arrow>`__
-  `Blessed <https://github.com/jquast/blessed>`__

Tested with: Python 2.7 & 3.4. Django 1.7.8 & 1.8.2


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

-  Make sure you have a `Redis <http://redis.io/>`__ server running
   somewhere

Read the more complete documentation at `http://django-q.readthedocs.org <http://django-q.readthedocs.org>`__


Configuration
~~~~~~~~~~~~~

All configuration settings are optional. e.g:

.. code:: python

    # settings.py
    Q_CLUSTER = {
        'name': 'myproject',
        'workers': 8,
        'recycle': 500,
        'timeout': 60,
        'compress': True,
        'save_limit': 250,
        'label': 'Django Q',
        'redis': {
            'host': '127.0.0.1',
            'port': 6379,
            'db': 0, }
    }

For full configuration options, see the `configuration documentation <http://django-q.readthedocs.org/en/latest/install.html#configuration>`__.


If you are using `django-redis <https://github.com/niwinz/django-redis>`__ , you can `configure <https://django-q.readthedocs.org/en/latest/install.html#django-redis>`__ Django Q to use its connection pool.

Management Commands
~~~~~~~~~~~~~~~~~~~

Start a cluster with::

    $ python manage.py qcluster

Monitor your clusters with::

    $ python manage.py qmonitor

Creating Tasks
~~~~~~~~~~~~~~

Use `async` from your code to quickly offload tasks:

.. code:: python

    from django_q import async, result

    # create the task
    async('math.copysign', 2, -2)

    # or with a reference
    import math.copysign

    task_id = async(copysign, 2, -2)

    # get the result
    task_result = result(task_id)

    # result returns None if the task has not been executed yet
    # so in most cases you will want to use a hook:

    async('math.modf', 2.5, hook='hooks.print_result')

    # hooks.py
    def print_result(task):
        print(task.result)


Schedule
~~~~~~~~

Schedules are regular Django models. You can manage them through the
Admin page or directly from your code:

.. code:: python

    from django_q import Schedule, schedule

    # Use the schedule function

    schedule('math.copysign',
             2, -2,
             hook='hooks.print_result',
             schedule_type=Schedule.DAILY)

    # Or create the object directly

    Schedule.objects.create(func='math.copysign',
                            hook='hooks.print_result',
                            args='2,-2',
                            schedule_type=Schedule.DAILY
                            )


Testing
~~~~~~~

To run the tests you will need `py.test <http://pytest.org/latest/>`__ and `pytest-django <https://github.com/pytest-dev/pytest-django>`__


Todo
~~~~

-  Write more sphinx `documentation <https://django-q.readthedocs.org>`__
-  Better tests and coverage
-  Get out of Alpha
-  Less dependencies?

Acknowledgements
~~~~~~~~~~~~~~~~

-  Django Q was inspired by working with
   `Django-RQ <https://github.com/ui/django-rq>`__ and
   `RQ <https://github.com/ui/django-rq>`__
-  Human readable hashes by
   `HumanHash <https://github.com/zacharyvoase/humanhash>`__

.. |image0| image:: https://travis-ci.org/Koed00/django-q.svg?branch=master
   :target: https://travis-ci.org/Koed00/django-q
.. |image1| image:: https://coveralls.io/repos/Koed00/django-q/badge.svg?branch=master
   :target: https://coveralls.io/r/Koed00/django-q?branch=master
.. |image2| image:: http://badges.gitter.im/Join%20Chat.svg
   :target: https://gitter.im/Koed00/django-q
.. |docs| image:: https://readthedocs.org/projects/docs/badge/?version=latest
    :alt: Documentation Status
    :scale: 100
    :target: https://django-q.readthedocs.org/
