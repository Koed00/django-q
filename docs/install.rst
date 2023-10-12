Installation
============
.. py:currentmodule:: django_q

-  Install the latest version with pip::

    $ pip install django-q2


-  Add :mod:`django_q` to ``INSTALLED_APPS`` in your projects :file:`settings.py`::

       INSTALLED_APPS = (
           # other apps
           'django_q',
       )

-  Run Django migrations to create the database tables::

    $ python manage.py migrate

-  Choose a message :doc:`broker<brokers>`, configure it and install the appropriate client library.

-  Run Django Q2 cluster in order to handle tasks async::

    $ python manage.py qcluster


Migrate from Django-Q to Django-Q2
----------------------------------

If you have an application with django-q running right now, you can simply swap the libraries and you should be good to go.::


    $ pip uninstall django-q # you might have to uninstall django-q add-ons as well
    $ pip install django-q2


Then migrate the database to get the latest tables/fields::

    $ python manage.py migrate


Requirements
------------

Django Q2 is tested for Python 3.8, 3.9, 3.10, 3.11 and 3.12

-  `Django <https://www.djangoproject.com>`__

    Django Q2 aims to use as much of Django's standard offerings as possible.
    The code is tested against Django versions `3.2.x`, `4.1.x`, `4.2.x` and `5.0.x`.

-  `Django-picklefield <https://github.com/gintas/django-picklefield>`__

    Used to store args, kwargs and result objects in the database.


Optional
~~~~~~~~
-  `Blessed <https://github.com/jquast/blessed>`__ is used to display the statistics in the terminal::

    $ pip install blessed

-  `Redis-py <https://github.com/andymccurdy/redis-py>`__ client by Andy McCurdy is used  to interface with both the Redis::

    $ pip install redis

.. _psutil_package:

- `Psutil <https://github.com/giampaolo/psutil>`__  python system and process utilities module by Giampaolo Rodola', is an optional requirement and adds cpu affinity settings to the cluster::

    $ pip install psutil

- `setproctitle <https://github.com/dvarrazzo/py-setproctitle>`__  python module to customize the process title by Daniele Varrazzo', is an optional requirement used to set informative process titles::

    $ pip install setproctitle

-  `Hiredis <https://github.com/redis/hiredis>`__ parser. This C library maintained by the core Redis team is faster than the standard PythonParser during high loads::

    $ pip install hiredis

- `Boto3 <https://github.com/boto/boto3>`__  is used for the Amazon SQS broker in favor of the now deprecating boto library::

    $ pip install boto3

- `Iron-mq <https://github.com/iron-io/iron_mq_python>`_ is the official python binding for the IronMQ broker::

    $ pip install iron-mq

- `Pymongo <https://github.com/mongodb/mongo-python-driver>`__ is needed if you want to use MongoDB as a message broker::

    $ pip install pymongo

- `Redis <http://redis.io/>`__ server is the default broker for Django Q2. It provides the best performance and does not require Django's cache framework for monitoring.

- `MongoDB <https://www.mongodb.org/>`__ is a highly scalable NoSQL database which makes for a very fast and reliably persistent at-least-once message broker. Usually available on most PaaS providers.

- `Pyrollbar <https://github.com/rollbar/pyrollbar>`__ is an error notifier for `Rollbar <https://rollbar.com/>`__  which lets you manage your worker errors in one place. Needs a `Rollbar <https://rollbar.com/>`__ account and access key::

    $ pip install rollbar




.. _croniter_package:

- `Croniter <https://github.com/kiorky/croniter>`__ is an optional package that is used to parse cron expressions for the scheduler::

    $ pip install croniter




Add-ons
-------
- `django-q-rollbar <https://github.com/danielwelch/django-q-rollbar>`__ is a Rollbar error reporter::

    $ pip install django-q2[rollbar]

- `django-q-sentry <https://github.com/danielwelch/django-q-sentry>`__ is a Sentry error reporter::

    $ pip install django-q2[sentry]

- `django-q-email <https://github.com/joeyespo/django-q-email>`__ is a compatible Django email backend that will automatically async queue your emails.


OS X
~~~~
Running Django Q2 on OS X should work fine, except for the following known issues:

* :meth:`multiprocessing.Queue.qsize()` is not supported. This leads to the monitor not reporting the internal queue size of clusters running under OS X.
* CPU count through :func:`multiprocessing.cpu_count()` does not work. Installing :ref:`psutil<psutil_package>` provides Django Q2 with an alternative way of determining the number of CPU's on your system
* CPU affinity is provided by :ref:`psutil<psutil_package>` which at this time does not support this feature on OSX. The code however is aware of this and will fake the CPU affinity assignment in the logs without actually assigning it. This way you can still develop with this setting.

Windows
~~~~~~~
The cluster and worker multiprocessing code depend on the OS's ability to fork, unfortunately forking is not supported under windows.
You should however be able to develop and test without the cluster by setting the ``sync`` option to ``True`` in the configuration.
This will run all ``async`` calls inline through a single cluster worker without the need for forking.
Other known issues are:

* :func:`os.getppid()` is only supported under windows since Python 3.2. If you use an older version you need to install :ref:`psutil<psutil_package>` as an alternative.
* CPU count through :func:`multiprocessing.cpu_count()` occasionally fails on servers. Installing :ref:`psutil<psutil_package>` provides Django Q2 with an alternative way of determining the number of CPU's on your system
* The monitor and info commands rely on the Curses package which is not officially supported on windows. There are however some ports available like `this one <http://www.lfd.uci.edu/~gohlke/pythonlibs/#curses>`__ by Christoph Gohlke.

Python
~~~~~~
Current tests are performed with 3.8, 3.9, 3.10, 3.11 and 3.12
If you do encounter any regressions with earlier versions, please submit an issue on `github <https://github.com/GDay/django-q2>`__

Open-source packages
~~~~~~~~~~~~~~~~~~~~
Django Q2 is always tested with the latest versions of the required and optional Python packages. We try to keep the dependencies as up to date as possible.
You can reference the `requirements <https://github.com/GDay/django-q2/blob/master/requirements.txt>`__ file to determine which versions are currently being used for tests and development.

Django
~~~~~~
We strive to be compatible with the last two major version of Django.
At the moment this means we support the 3.2.x, 4.1.x, 4.2.x and 5.0.x releases.

Since we are now no longer supporting Python 2, we can also not support older versions of Django that do not support Python >= 3.8
For this you can always use older releases, but they are no longer maintained.
