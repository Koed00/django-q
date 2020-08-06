Installation
============
.. py:currentmodule:: django_q

-  Install the latest version with pip::

    $ pip install django-q


-  Add :mod:`django_q` to ``INSTALLED_APPS`` in your projects :file:`settings.py`::

       INSTALLED_APPS = (
           # other apps
           'django_q',
       )

-  Run Django migrations to create the database tables::

    $ python manage.py migrate

-  Choose a message :doc:`broker<brokers>` , configure it and install the appropriate client library.

-  Run Django Q cluster in order to handle tasks async::

    $ python manage.py qcluster

Requirements
------------

Django Q is tested for Python 3.7 and 3.8

-  `Django <https://www.djangoproject.com>`__

    Django Q aims to use as much of Django's standard offerings as possible
    The code is tested against Django versions `2.2.x` and `3.1.x`.
    Please note that Django versions below 2.0 do not support Python 3.7

-  `Django-picklefield <https://github.com/gintas/django-picklefield>`__

    Used to store args, kwargs and result objects in the database.

-  `Arrow <https://github.com/crsmithdev/arrow>`__

    The scheduler uses Chris Smith's wonderful project to determine correct dates in the future.

-  `Blessed <https://github.com/jquast/blessed>`__

    This feature-filled fork of Erik Rose's blessings project provides the terminal layout of the monitor.


Optional
~~~~~~~~
-  `Redis-py <https://github.com/andymccurdy/redis-py>`__ client by Andy McCurdy is used  to interface with both the Redis and Disque brokers::

    $ pip install redis

.. _psutil_package:

- `Psutil <https://github.com/giampaolo/psutil>`__  python system and process utilities module by Giampaolo Rodola', is an optional requirement and adds cpu affinity settings to the cluster::

    $ pip install psutil

-  `Hiredis <https://github.com/redis/hiredis>`__ parser. This C library maintained by the core Redis team is faster than the standard PythonParser during high loads::

    $ pip install hiredis

- `Boto3 <https://github.com/boto/boto3>`__  is used for the Amazon SQS broker in favor of the now deprecating boto library::

    $ pip install boto3

- `Iron-mq <https://github.com/iron-io/iron_mq_python>`_ is the official python binding for the IronMQ broker::

    $ pip install iron-mq

- `Pymongo <https://github.com/mongodb/mongo-python-driver>`__ is needed if you want to use MongoDB as a message broker::

    $ pip install pymongo

- `Redis <http://redis.io/>`__ server is the default broker for Django Q. It provides the best performance and does not require Django's cache framework for monitoring.

- `Disque <https://github.com/antirez/disque>`__ server is based on Redis by the same author, but focuses on reliable queues. Currently in Alpha, but highly recommended. You can either build it from source or use it on Heroku through the `Tynd <https://disque.tynd.co/>`__ beta.

- `MongoDB <https://www.mongodb.org/>`__ is a highly scalable NoSQL database which makes for a very fast and reliably persistent at-least-once message broker. Usually available on most PaaS providers.

- `Pyrollbar <https://github.com/rollbar/pyrollbar>`__ is an error notifier for `Rollbar <https://rollbar.com/>`__  which lets you manage your worker errors in one place. Needs a `Rollbar <https://rollbar.com/>`__ account and access key::

    $ pip install rollbar




.. _croniter_package:

- `Croniter <https://github.com/kiorky/croniter>`__ is an optional package that is used to parse cron expressions for the scheduler::

    $ pip install croniter




Add-ons
-------
- `django-q-rollbar <https://github.com/danielwelch/django-q-rollbar>`__ is a Rollbar error reporter::

    $ pip install django-q[rollbar]

- `django-q-sentry <https://github.com/danielwelch/django-q-sentry>`__ is a Sentry error reporter::

    $ pip install django-q[sentry]

- `django-q-email <https://github.com/joeyespo/django-q-email>`__ is a compatible Django email backend that will automatically async queue your emails.

Compatibility
-------------
Django Q is still a young project. If you do find any incompatibilities please submit an issue on `github <https://github.com/Koed00/django-q>`__.

OS X
~~~~
Running Django Q on OS X should work fine, except for the following known issues:

* :meth:`multiprocessing.Queue.qsize()` is not supported. This leads to the monitor not reporting the internal queue size of clusters running under OS X.
* CPU count through :func:`multiprocessing.cpu_count()` does not work. Installing :ref:`psutil<psutil_package>` provides Django Q with an alternative way of determining the number of CPU's on your system
* CPU affinity is provided by :ref:`psutil<psutil_package>` which at this time does not support this feature on OSX. The code however is aware of this and will fake the CPU affinity assignment in the logs without actually assigning it. This way you can still develop with this setting.

Windows
~~~~~~~
The cluster and worker multiprocessing code depend on the OS's ability to fork, unfortunately forking is not supported under windows.
You should however be able to develop and test without the cluster by setting the ``sync`` option to ``True`` in the configuration.
This will run all ``async`` calls inline through a single cluster worker without the need for forking.
Other known issues are:

* :func:`os.getppid()` is only supported under windows since Python 3.2. If you use an older version you need to install :ref:`psutil<psutil_package>` as an alternative.
* CPU count through :func:`multiprocessing.cpu_count()` occasionally fails on servers. Installing :ref:`psutil<psutil_package>` provides Django Q with an alternative way of determining the number of CPU's on your system
* The monitor and info commands rely on the Curses package which is not officially supported on windows. There are however some ports available like `this one <http://www.lfd.uci.edu/~gohlke/pythonlibs/#curses>`__ by Christoph Gohlke.

Python
~~~~~~
The code is always tested against the latest version Python 3 and we try to stay compatible with the last two versions of each.
Current tests are performed with 3.7 and 3.8
If you do encounter any regressions with earlier versions, please submit an issue on `github <https://github.com/Koed00/django-q>`__

.. note::

    Django releases before 1.11 are not supported on Python 3.6
    Django releases before 2.0 are not supported on Python 3.7

Open-source packages
~~~~~~~~~~~~~~~~~~~~
Django Q is always tested with the latest versions of the required and optional Python packages. We try to keep the dependencies as up to date as possible.
You can reference the `requirements <https://github.com/Koed00/django-q/blob/master/requirements.txt>`__ file to determine which versions are currently being used for tests and development.

Django
~~~~~~
We strive to be compatible with last two major version of Django.
At the moment this means we support the 2.2.x and 3.1.x releases.

Since we are now no longer supporting Python 2, we can also not support older versions of Django that do not support Python >= 3.6
For this you can always use older releases, but they are no longer maintained.



