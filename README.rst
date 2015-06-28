Django Q
========

A multiprocessing task queue for Django
---------------------------------------

|image0|

Features
~~~~~~~~

-  Multiprocessing worker pool
-  Encrypted and compressed task packages
-  Scheduled tasks
-  Result hooks
-  Result and Failure database
-  PaaS compatible with multiple pools
-  Django Admin

Requirements
~~~~~~~~~~~~

-  `Redis-py <https://github.com/andymccurdy/redis-py>`__
-  `Django <https://www.djangoproject.com>`__ > = 1.7
-  `Django-picklefield <https://github.com/gintas/django-picklefield>`__
-  `Arrow <https://github.com/crsmithdev/arrow>`__
-  `Blessed <https://github.com/jquast/blessed>`__

Tested with: Python 2.7, 3.4. Django 1.7.8, 1.8.2\*

\*\ *Django Q is currently in Alpha and as such not safe for production,
yet.*

Installation
~~~~~~~~~~~~

-  Install the latest version with pip: ``pip install django-q``
-  Add ``django_q`` to ``INSTALLED_APPS`` in your settings.py:

   .. code:: python

       INSTALLED_APPS = (
           # other apps
           'django_q',
       )

-  Run ``python manage.py migrate`` to create the database tables
-  Make sure you have a `Redis <http://redis.io/>`__ server running
   somewhere

Configuration
~~~~~~~~~~~~~

All configuration settings are optional. e.g:

.. code:: python

    # settings.py
    Q_CLUSTER = {
        'name': 'myproject', 
        'workers': 8, 
        'recycle': 500,
        'compress': True,
        'save_limit': 250,
        'label': 'Django Q',
        'redis': {
            'host': '127.0.0.1',
            'port': 6379,
            'db': 0, }
    }

-  **name** Used to differentiatie between projects using the same Redis
   server\* *default*: 'default'

-  **workers** The number of workers to use in the cluster *default*:
   CPU count of host

-  **recycle** The number of tasks a worker will process before
   respawing. Used to release resources. *default*: 500

-  **compress** Compress task packages to Redis. Useful for large
   payloads. *default*: False

-  **save\_limit** Limits the amount of successful tasks saved to
   Django. Set to 0 for unlimited. Set to -1 for no success storage at
   all. Failures are always saved. *default*: 250

-  **label** The label used for the Django Admin page *default*: 'Django
   Q'

-  **redis** Connection settings for Redis. Follows standard Redis-Py
   syntax. *default*: localhost

\*\ *Django Q uses your SECRET\_KEY to encrypt task packages and prevent
task crossover*

Managment Commands
~~~~~~~~~~~~~~~~~~

qcluster
^^^^^^^^

Start a cluster with: ``python manage.py qcluster`` ####qmonitor Monitor
your clusters with ``python manage.py qmonitor``

Creating Tasks
~~~~~~~~~~~~~~

Async
^^^^^

.. code:: python

    async(func,*args,hook=None,**kwargs)

.. code:: python

    from django_q import async, result

    # create the task
    async('math.copysign', 2, -2)

    # or with import and storing the id
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
^^^^^^^^

Schedules are regular Django models. You can manage them through the
Admin page or in your code:

.. code:: python

    from django_q import Schedule
    from django.utils import timezone

    Schedule.create(func='math.copysign', 
                    hook='hooks.print_result', 
                    args='2,-2', 
                    schedule_type=Schedule.DAILY,
                    next_run=timezone.now())

Todo
----

-  Write sphinx documentation
-  Better tests and coverage
-  Get out of Alpha
-  Less dependencies?

.. |image0| image:: https://travis-ci.org/Koed00/django-q.svg?branch=master
   :target: https://travis-ci.org/Koed00/django-q
