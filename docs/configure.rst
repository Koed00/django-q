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

Used to differentiate between projects using the same broker.
On most broker types this will be used as the queue name.
Defaults to ``'default'``.

.. note::
    Tasks are encrypted. When a worker encounters a task it can not decrypt, it will be discarded or failed.

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

.. _retry:

retry
~~~~~

The number of seconds a broker will wait for a cluster to finish a task, before it's presented again.
Only works with brokers that support delivery receipts. Defaults to 60 seconds.

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

This does not limit the amount of tasks that can be queued on the broker, but rather how many tasks are kept in memory by a single cluster.
Setting this to a reasonable number, can help balance the workload and the memory overhead of each individual cluster.
Defaults to ``workers**2``.

label
~~~~~

The label used for the Django Admin page. Defaults to ``'Django Q'``

.. _catch_up:

catch_up
~~~~~~~~
The default behavior for schedules that didn't run while a cluster was down, is to play catch up and execute all the missed time slots until things are back on schedule.
You can override this behavior by setting ``catch_up`` to ``False``. This will make those schedules run only once when the cluster starts and normal scheduling resumes.
Defaults to ``True``.

.. _redis_configuration:

redis
~~~~~

Connection settings for Redis. Defaults::

    # redis defaults
    Q_CLUSTER = {
        'redis': {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'password': None,
            'socket_timeout': None,
            'charset': 'utf-8',
            'errors': 'strict',
            'unix_socket_path': None
        }
    }

For more information on these settings please refer to the `Redis-py <https://github.com/andymccurdy/redis-py>`__ documentation

.. _django_redis:

django_redis
~~~~~~~~~~~~

If you are already using `django-redis <https://github.com/niwinz/django-redis>`__ for your caching, you can take advantage of its excellent connection backend by supplying the name
of the cache connection you want to use instead of a direct Redis connection::

    # example django-redis connection
    Q_CLUSTER = {
        'name': 'DJRedis',
        'workers': 4,
        'timeout': 90,
        'django_redis': 'default'
    }



.. tip::
    Django Q uses your ``SECRET_KEY`` to encrypt task packages and prevent task crossover. So make sure you have it set up in your Django settings.

.. _disque_configuration:

disque_nodes
~~~~~~~~~~~~
If you want to use Disque as your broker, set this to a list of available Disque nodes and each cluster will randomly try to connect to them::

    # example disque connection
    Q_CLUSTER = {
        'name': 'DisqueBroker',
        'workers': 4,
        'timeout': 60,
        'retry': 60,
        'disque_nodes': ['127.0.0.1:7711', '127.0.0.1:7712']
    }


Django Q is also compatible with the `Tynd Disque <https://disque.tynd.co/>`__  addon on `Heroku <https://heroku.com>`__::

    # example Tynd Disque connection
    import os

    Q_CLUSTER = {
        'name': 'TyndBroker',
        'workers': 8,
        'timeout': 30,
        'retry': 60,
        'bulk': 10,
        'disque_nodes': os.environ['TYND_DISQUE_NODES'].split(','),
        'disque_auth': os.environ['TYND_DISQUE_AUTH']
    }


disque_auth
~~~~~~~~~~~

Optional Disque password for servers that require authentication.

.. _ironmq_configuration:

iron_mq
~~~~~~~
Connection settings for IronMQ::

    # example IronMQ connection

    Q_CLUSTER = {
        'name': 'IronBroker',
        'workers': 8,
        'timeout': 30,
        'retry': 60,
        'queue_limit': 50,
        'bulk': 10,
        'iron_mq': {
            'host': 'mq-aws-us-east-1.iron.io',
            'token': 'Et1En7.....0LuW39Q',
            'project_id': '500f7b....b0f302e9'
        }
    }


All connection keywords are supported. See the `iron-mq <https://github.com/iron-io/iron_mq_python#configure>`__ library for more info

bulk
~~~~
Sets the number of messages each cluster tries to get from the broker per call. Setting this on supported brokers can improve performance.
Especially HTTP based or very high latency servers can benefit from bulk dequeue.
Keep in mind however that settings this too high can degrade performance with multiple clusters or very large task packages.

Not supported by the default Redis broker.
Defaults to 1.

cache
~~~~~
For some brokers, you will need to set up the Django `cache framework <https://docs.djangoproject.com/en/1.8/topics/cache/#setting-up-the-cache>`__
to gather statistics for the monitor. You can indicate which cache to use by setting this value. Defaults to ``default``.

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

    *Psutil does not support cpu affinity on OS X at this time.*

.. py:module:: django_q

.. rubric:: Footnotes

.. [#f1] Uses :func:`multiprocessing.cpu_count()` which can fail on some platforms. If so , please set the worker count in the configuration manually or install :ref:`psutil<psutil>` to provide an alternative cpu count method.
