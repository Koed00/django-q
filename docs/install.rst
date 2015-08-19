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

-  Make sure you have a `Redis <http://redis.io/>`__ server running
   somewhere and know how to connect to it.

Requirements
------------

Django Q is tested for Python 2.7 and 3.4

-  `Django <https://www.djangoproject.com>`__

    Django Q aims to use as much of Django's standard offerings as possible
    The code is tested against Django version `1.7.9` and `1.8.3`.

-  `Django-picklefield <https://github.com/gintas/django-picklefield>`__

    Used to store args, kwargs and result objects in the database.

-  `Redis-py <https://github.com/andymccurdy/redis-py>`__

    Andy McCurdy's excellent Redis python client.

-  `Arrow <https://github.com/crsmithdev/arrow>`__

    The scheduler uses Chris Smith's wonderful project to determine correct dates in the future.

-  `Blessed <https://github.com/jquast/blessed>`__

    This feature-filled fork of Erik Rose's blessings project provides the terminal layout of the monitor.

-  `Redis server <http://redis.io/>`__

    Django Q uses Redis as a centralized hub between your Django instances and your Q clusters.


Optional
~~~~~~~~
.. _psutil:

- `Psutil <https://github.com/giampaolo/psutil>`__  python system and process utilities module by Giampaolo Rodola', is an optional requirement and adds cpu affinity settings to the cluster::

    $ pip install psutil


-  `Hiredis <https://github.com/redis/hiredis>`__ parser. This C library maintained by the core Redis team is faster than the standard PythonParser during high loads::

    $ pip install hiredis

