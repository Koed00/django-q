.. Django Q documentation master file, created by
   sphinx-quickstart on Fri Jun 26 22:18:36 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Django Q2
====================
Django Q2 is a native Django task queue, scheduler and worker application using Python multiprocessing.

.. note::
    Django Q2 is a fork of Django Q. Big thanks to Ilan Steemers for starting this project. Unfortunately, development of Django Q has stalled since June 2021. Django Q2 is the new updated version of Django Q, with dependencies updates, docs updates and several bug fixes. Original repository: https://github.com/Koed00/django-q


Features
--------

-  Multiprocessing worker pools
-  Asynchronous tasks
-  Scheduled, cron and repeated tasks
-  Signed and compressed packages
-  Failure and success database or cache
-  Result hooks, groups and chains
-  Django Admin integration
-  PaaS compatible with multiple instances
-  Multi cluster monitor
-  Redis, IronMQ, SQS, MongoDB or ORM
-  Rollbar and Sentry support


Django Q2 is tested with: Python 3.8, 3.9, 3.10, 3.11 and 3.12. Works with Django 3.2.x, 4.1.x, 4.2.x and 5.0.x

Currently available in English, German and French.

Contents:

.. toctree::
   :maxdepth: 2

    Installation <install>
    Configuration <configure>
    Brokers <brokers>
    Tasks <tasks>
    Groups <group>
    Iterable <iterable>
    Chains <chain>
    Schedules <schedules>
    Cluster <cluster>
    Monitor <monitor>
    Admin <admin>
    Errors <errors>
    Signals <signals>
    Architecture <architecture>
    Examples <examples>

* :ref:`genindex`
