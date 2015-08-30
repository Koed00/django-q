Configuration
-------------
.. py:currentmodule:: django_q

Configuration is handled via the ``Q_CLUSTER`` dictionary in your :file:`settings.py`

.. code:: python

    # settings.py example
    Q_CLUSTER = {
        'name': 'myproject',
        'workers': 8,
        'recycle': 500,
        'timeout': 60,
        'compress': True,
        'save_limit': 250,
        'queue_limit': 500,
        'cpu_affinity': 1,
        'label': 'Django Q',
        'redis': {
            'host': '127.0.0.1',
            'port': 6379,
            'db': 0, }
    }

All configuration settings are optional:

name
~~~~

Used to differentiate between projects using the same Redis server. Defaults to ``'default'``.
This can be useful if you have several projects using the same Redis server.

.. note::
    Tasks are encrypted. When a worker encounters a task it can not decrypt, it will be discarded.

workers
~~~~~~~

The number of workers to use in the cluster. Defaults to CPU count of the current host, but can be set to a custom number.  [#f1]_

recycle
~~~~~~~

The number of tasks a worker will process before recycling . Useful to release memory resources on a regular basis. Defaults to ``500``.

.. _timeout:

timeout
~~~~~~~

The number of seconds a worker is allowed to spend on a task before it's terminated. Defaults to ``None``, meaning it will never time out.
Set this to something that makes sense for your project. Can be overridden for individual tasks.

compress
~~~~~~~~

Compresses task packages to Redis. Useful for large payloads, but can add overhead when used with many small packages.
Defaults to ``False``

.. _save_limit:

save_limit
~~~~~~~~~~

Limits the amount of successful tasks saved to Django.
 - Set to ``0`` for unlimited.
 - Set to ``-1`` for no success storage at all.
 - Defaults to ``250``
 - Failures are always saved.

.. _sync:

sync
~~~~

When set to ``True`` this configuration option forces all :func:`async` calls to be run with ``sync=True``.
Effectively making everything synchronous. Useful for testing. Defaults to ``False``.

.. _queue_limit:

queue_limit
~~~~~~~~~~~

This does not limit the amount of tasks that can be queued overall on Redis, but rather how many tasks are kept in memory by a single cluster.
Setting this to a reasonable number, can help balance the workload and the memory overhead of each individual cluster.
It can also be used to manage the loss of data in case of a cluster failure.
Defaults to ``None``, meaning no limit.

label
~~~~~

The label used for the Django Admin page. Defaults to ``'Django Q'``

.. _catch_up:

catch_up
~~~~~~~~
The default behavior for schedules that didn't run while a cluster was down, is to play catch up and execute all the missed time slots until things are back on schedule.
You can override this behavior by setting ``catch_up`` to ``False``. This will make those schedules run only once when the cluster starts and normal scheduling resumes.
Defaults to ``True``.

redis
~~~~~

Connection settings for Redis. Defaults::

    redis: {
        'host': 'localhost',
        'port': 6379,
        'db': 0,
        'password': None,
        'socket_timeout': None,
        'charset': 'utf-8',
        'errors': 'strict',
        'unix_socket_path': None
    }

For more information on these settings please refer to the `Redis-py <https://github.com/andymccurdy/redis-py>`__ documentation

.. _django_redis:

django_redis
~~~~~~~~~~~~

If you are already using `django-redis <https://github.com/niwinz/django-redis>`__ for your caching, you can take advantage of its excellent connection backend by supplying the name
of the cache connection you want to use::

    # example django-redis connection
    Q_CLUSTER = {
        'name': 'DJRedis',
        'workers': 4,
        'timeout': 90,
        'django_redis: 'default'
    }



.. tip::
    Django Q uses your ``SECRET_KEY`` to encrypt task packages and prevent task crossover. So make sure you have it set up in your Django settings.

cpu_affinity
~~~~~~~~~~~~

Sets the number of processor each worker can use. This does not affect auxiliary processes like the sentinel or monitor and is only useful for tweaking the performance of very high traffic clusters.
The affinity number has to be higher than zero and less than the total number of processors to have any effect. Defaults to using all processors::

    # processor affinity example.

    4 processors, 4 workers, cpu_affinity: 1

    worker 1 cpu [0]
    worker 2 cpu [1]
    worker 3 cpu [2]
    worker 4 cpu [3]

    4 processors, 4 workers, cpu_affinity: 2

    worker 1 cpu [0, 1]
    worker 2 cpu [2, 3]
    worker 3 cpu [0, 1]
    worker 4 cpu [2, 3]

    8 processors, 8 workers, cpu_affinity: 3

    worker 1 cpu [0, 1, 2]
    worker 2 cpu [3, 4, 5]
    worker 3 cpu [6, 7, 0]
    worker 4 cpu [1, 2, 3]
    worker 5 cpu [4, 5, 6]
    worker 6 cpu [7, 0, 1]
    worker 7 cpu [2, 3, 4]
    worker 8 cpu [5, 6, 7]


In some cases, setting the cpu affinity for your workers can lead to performance improvements, especially if the load is high and consists of many repeating small tasks.
Start with an affinity of 1 and work your way up. You will have to experiment with what works best for you.
As a rule of thumb; cpu_affinity 1 favors repetitive short running tasks, while no affinity benefits longer running tasks.

.. note::

    The ``cpu_affinity`` setting requires the optional :ref:`psutil <psutil>` module.

.. py:module:: django_q

.. rubric:: Footnotes

.. [#f1] Uses :func:`multiprocessing.cpu_count()` which can fail on some platforms. If so , please set the worker count in the configuration manually or install :ref:`psutil<psutil>` to provide an alternative cpu count method.