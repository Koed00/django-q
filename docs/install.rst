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


Requirements
------------

Django Q is tested for Python 2.7 and 3.4

-  `Django <https://www.djangoproject.com>`__

    Django Q aims to use as much of Django's standard offerings as possible
    The code is tested against Django version `1.7.10` and `1.8.4`.

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

.. _psutil:

- `Psutil <https://github.com/giampaolo/psutil>`__  python system and process utilities module by Giampaolo Rodola', is an optional requirement and adds cpu affinity settings to the cluster::

    $ pip install psutil

-  `Hiredis <https://github.com/redis/hiredis>`__ parser. This C library maintained by the core Redis team is faster than the standard PythonParser during high loads::

    $ pip install hiredis

- `Boto3 <https://github.com/boto/boto3>`__  is used for the Amazon SQS broker in favor of the now deprecating boto library::

    $ pip install boto3

- `Iron-mq <https://github.com/iron-io/iron_mq_python>`_ is the official python binding for the IronMQ broker::

    $ pip install iron-mq

- `Redis <http://redis.io/>`__ server is the default broker for Django Q. It provides the best performance and does not require Django's cache framework for monitoring.

- `Disque <https://github.com/antirez/disque>`__ server is based on Redis by the same author, but focuses on reliable queues. Currently in Alpha, but highly recommended. You can either build it from source or use it on Heroku through the `Tynd <https://disque.tynd.co/>`__ beta.
