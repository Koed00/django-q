Installation
============

-  Install the latest version with pip::

    $ pip install django-q


-  Add :mod:`django_q` to your :const:`INSTALLED_APPS` in your projects :file:`settings.py`::

       INSTALLED_APPS = (
           # other apps
           'django_q',
       )

-  Run Django migrations to create the database tables::

    $ python manage.py migrate

-  Make sure you have a `Redis <http://redis.io/>`__ server running
   somewhere

Configuration
-------------

Configuration is handled via the :const:`Q_ClUSTER` dictionary in your :file:`settings.py`

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
    Tasks are encrypted. When a worker encounters a task it can not decrypt, it will be discarded

workers
~~~~~~~

The number of workers to use in the cluster. Defaults to CPU count of the current host, but can be set to a custom number.

recycle
~~~~~~~

The number of tasks a worker will process before respawning. Useful to release resources on a regular basis. Defaults to ``500``.

timeout
~~~~~~~

The number of seconds a worker is allowed to spend on a task before it's terminated. Defaults to ``None``, meaning it will never time out.
Set this to something that makes sense for your use

compress
~~~~~~~~

Compress task packages to Redis. Useful for large payloads, but can add overhead when used with many small packages.
Defaults to ``False``

save_limit
~~~~~~~~~~

Limits the amount of successful tasks saved to Django.
Set to ``0`` for unlimited. Set to ``-1`` for no success storage at all.
Failures are always saved. Defaults to ``250``

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


.. note::
    Django Q uses your :const:`SECRET_KEY` to encrypt task packages and prevent task crossover. So make sure you have it set up in your Django settings.

