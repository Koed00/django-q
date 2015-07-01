Django Q
========

A multiprocessing task queue for Django
---------------------------------------

|image0| |image1| |image2|

Features
~~~~~~~~

-  Multiprocessing worker pool
-  Encrypted and compressed task packages
-  Scheduled tasks
-  Result hooks
-  Failure and result database
-  PaaS compatible with multiple instances
-  Django Admin integration
-  Multi cluster monitor

Requirements
~~~~~~~~~~~~

-  `Redis-py <https://github.com/andymccurdy/redis-py>`__
-  `Django <https://www.djangoproject.com>`__ > = 1.7
-  `Django-picklefield <https://github.com/gintas/django-picklefield>`__
-  `Arrow <https://github.com/crsmithdev/arrow>`__
-  `Blessed <https://github.com/jquast/blessed>`__

Tested with: Python 2.7, 3.4. Django 1.7.8, 1.8.2\*

\*\ *Django Q is currently  in Alpha and as such not safe for production,
yet.*

Installation
~~~~~~~~~~~~

-  Install the latest version with pip: ``pip install django-q``
-  Add `django_q` to `INSTALLED_APPS` in your settings.py:

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
        'timeout': 60,
        'compress': True,
        'save_limit': 250,
        'label': 'Django Q',
        'redis': {
            'host': '127.0.0.1',
            'port': 6379,
            'db': 0, }
    }

-  **name**: Used to differentiate between projects using the same Redis
   server\*. Defaults to 'default'.

-  **workers**: The number of workers to use in the cluster. Defaults to CPU count.

-  **recycle**: The number of tasks a worker will process before
   respawning. Used to release resources. Defaults to 500

-  **timeout**: The number of seconds a worker is allowed to spend on a task before it's terminated. Defaults to None.

-  **compress**: Compress task packages to Redis. Useful for large
   payloads. Defaults to False

-  **save\_limit**: Limits the amount of successful tasks saved to
   Django. Set to 0 for unlimited. Set to -1 for no success storage at
   all. Failures are always saved. Defaults to 250

-  **label**: The label used for the Django Admin page. Defaults to 'Django Q'

-  **redis**: Connection settings for Redis. Follows standard Redis-Py syntax. Defaults to standard localhost.


\*\ *Django Q uses your SECRET\_KEY to encrypt task packages and prevent
task crossover*

Management Commands
~~~~~~~~~~~~~~~~~~~

qcluster
^^^^^^^^

Start a cluster with: ``python manage.py qcluster``

qmonitor
^^^^^^^^

Monitor your clusters with ``python manage.py qmonitor``

Creating Tasks
~~~~~~~~~~~~~~

Async
^^^^^

Use async from your code to quickly offload tasks:

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

.. code:: python

    async(func,*args,**kwargs)

- **func**: Function to execute. Dotted string or reference.
- **args**: Optional arguments for the function.
- **hook**: Optional function to call after execution. Dotted string or reference.
- **kwargs**: Optional keyword arguments for the function.

Schedule
^^^^^^^^

Schedules are regular Django models. You can manage them through the
Admin page or directly from your code:

.. code:: python

    from django_q import Schedule, schedule

    # Use the schedule wrapper

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

.. code:: python

    schedule(func,*args,**kwargs)

- **func**: the function to schedule. Dotted strings only.
- **args**: arguments for the scheduled function.
- **hook**: optional result hook function. Dotted strings only.
- **schedule_type**: (O)nce, (H)ourly, (D)aily, (W)eekly, (M)onthly, (Q)uarterly, (Y)early
- **repeats**: Number of times to repeat schedule. -1=Always, 0=Never, n=n.
- **next_run**: Next or first scheduled execution datetime.
- **kwargs**: optional keyword arguments for the scheduled function.


Models
~~~~~~
- `Task` and `Schedule` are Django Models and can therefore be managed by your own code.----------------
- `Task` objects are only created after an async package has been executed.
-  A `Schedule` creates a new async package for every execution and thus an unique `Task`
- `Success` and `Failure` are convenient proxy models of `Task`


Testing
~~~~~~~

To run the tests you will need `py.test <http://pytest.org/latest/>`__ and `pytest-django <https://github.com/pytest-dev/pytest-django>`__


Todo
~~~~

-  Write sphinx documentation
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