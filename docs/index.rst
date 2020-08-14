.. Django Q documentation master file, created by
   sphinx-quickstart on Fri Jun 26 22:18:36 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Django Q
===================
Django Q is a native Django task queue, scheduler and worker application using Python multiprocessing.


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
-  Redis, Disque, IronMQ, SQS, MongoDB or ORM
-  Rollbar and Sentry support


Django Q is tested with: Python 3.7 and 3.8, Django 2.2.x and 3.1.x


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
* :ref:`search`

