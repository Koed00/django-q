Installation
============

-  Install the latest version with pip::

    $ pip install django-q


-  Add :mod:`django_q` to `INSTALLED_APPS` in your projects :file:`settings.py`::

       INSTALLED_APPS = (
           # other apps
           'django_q',
       )

-  Run Django migrations to create the database tables::

    $ python manage.py migrate

-  Make sure you have a `Redis <http://redis.io/>`__ server running
   somewhere

.. _configuration:

Configuration
-------------

Configuration is handled via the `Q_ClUSTER` dictionary in your :file:`settings.py`

.. code:: python

    # settings.py example
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



name
~~~~

Used to differentiate between projects using the same Redis server. Defaults to ``'default'``.
This can be useful if you have several projects using the same Redis server.

.. note::
    Tasks are encrypted. When a worker encounters a task it can not decrypt, it will be discarded.

workers
~~~~~~~

The number of workers to use in the cluster. Defaults to CPU count of the current host, but can be set to a custom number.

recycle
~~~~~~~

The number of tasks a worker will process before recycling . Useful to release memory resources on a regular basis. Defaults to ``500``.

timeout
~~~~~~~

The number of seconds a worker is allowed to spend on a task before it's terminated. Defaults to ``None``, meaning it will never time out.
Set this to something that makes sense for your project.

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

label
~~~~~

The label used for the Django Admin page. Defaults to ``'Django Q'``

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
    Django Q uses your `SECRET_KEY` to encrypt task packages and prevent task crossover. So make sure you have it set up in your Django settings.

Requirements
------------

Django Q is tested for Python 2.7 and 3.4

-  `Django <https://www.djangoproject.com>`__

    Django Q aims to use as much of Django's standard offerings as possible
    The code is tested against Django version `1.7.8` and `1.8.2`.

-  `Django-picklefield <https://github.com/gintas/django-picklefield>`__

    Used to store args, kwargs and result objects in the database.

-  `Redis-py <https://github.com/andymccurdy/redis-py>`__

    Andy McCurdy's excellent Redis python client.

-  `Arrow <https://github.com/crsmithdev/arrow>`__

    The scheduler uses Chris Smith's wonderful project to determine correct dates in the future.

-  `Blessed <https://github.com/jquast/blessed>`__

    This feature-filled fork of Erik Rose's blessings project provides the terminal layout of the monitor.


.. tip::

    Install the `Hiredis <https://github.com/redis/hiredis>`__ parser::

    $ pip install hiredis

    This C library maintained by the core Redis team is faster than the standard PythonParser during high loads.

.. py:module:: django_q