Django Q
========

A multiprocessing task queue application for Django
---------------------------------------------------

|image0| ### Status In Alpha. Everything should work, but the basic
structure can still change. Main focus is on creating more tests, better
coverage and stability.

Architecture
~~~~~~~~~~~~

.. figure:: http://i.imgur.com/wTIeg2T.png
   :alt: Django Q schema

   Django Q schema
Usage
~~~~~

Schedule the asynchronous execution of a function by calling ``async``
from within your Django project.

.. code:: python

    async(func,*args,hook=None,**kwargs)

Basic example
^^^^^^^^^^^^^

.. code:: python

    from django_q import async

    # math.copysign(2,-2)
    async('math.copysign', 2, -2)

    # also
    from math import copysign

    async(copysign, 2, -2)

Result example
^^^^^^^^^^^^^^

.. code:: python

    from django_q import async, result

    # create the task
    task_id = async('math.copysign', 2, -2)

    # get the result
    task_result = result(task_id)

    # result returns None if the task has not been executed yet
    # so it makes more sense to use a hook:

    async('math.modf', 2.5, hook='hooks.print_result')

    # hooks.py
    def print_result(task):
        print(task.result)

Management commands
~~~~~~~~~~~~~~~~~~~

``qcluster``
^^^^^^^^^^^^

Start a cluster with ``./manage.py qcluster``

.. figure:: http://i.imgur.com/xccUxhW.png
   :alt: qcluster command

   qcluster command
``qmonitor``
^^^^^^^^^^^^

You can monitor basic information about all the connected clusters by
running ``./manage.py qmonitor``

.. figure:: http://i.imgur.com/5cm7hdP.png
   :alt: qmonitor command

   qmonitor command
Admin integration
~~~~~~~~~~~~~~~~~

Django Q registers itself with the admin page to show failed, successful
and scheduled tasks. From there task results can be read or deleted. If
necessary, failed tasks can be reintroduced to the queue. Schedules be
created and their results monitored. |q admin|

Schedules
~~~~~~~~~

Scheduled tasks are a django model and can be created through the admin
interface or by creating a Schedule instance directly. Like the Async
Task, a Schedule can take an optional hook keyword and is used as a
template to create the actual task package at the scheduled time. If a
result task is available in the database, it can be accessed through the
Schedule instance's ``result()`` method.

Signed Tasks
~~~~~~~~~~~~

Tasks are first pickled to Json and then signed using Django's own
signing module before being sent to a Redis list. This ensures that task
packages on the Redis server can only be excuted and read by clusters
and django servers who share the same secret key.

Optionally, packages can be compressed before transport by setting
``Q_COMPRESSED = True``

Pusher
~~~~~~

The pusher process continuously checks the Redis list for new task
packages and pushes them on the Task Queue.

Worker
~~~~~~

A worker process checks the package signing, unpacks the task, executes
it and saves the return value. Irrespective of the failure or success of
any of these steps, the package is then pushed onto the Result Queue.

By default Django Q spawns a worker for each detected CPU on the host
system. This can be overridden by setting ``Q_WORKERS =  n``. With *n*
being the number of desired worker processes.

Monitor
~~~~~~~

The result monitor checks the Result Queue for processed packages and
saves both failed and successful packages to the Django database.

By default only the last 100 successful packages are kept in the
database. This can be increased or decreased at will by settings
``Q_SAVE_LIMIT = n``. With *n* being the desired number of records. Set
``Q_SAVE_LIMIT = 0`` to save all results to the database. Failed
packages are always saved.

Sentinel
~~~~~~~~

The sentinel spawns all process and then checks the health of all
workers, including the pusher and the monitor. Reincarnating processes
if any may fail. In case of a stop signal, the sentinel will halt the
pusher and instruct the workers and monitor to finish the remaining
items , before exiting.

Hooks
~~~~~

Packages can be assigned a hook function, upon completion of the package
this function will be called with the Task object as the first argument.

Todo
~~~~

I'll add to this README while I'm developing the various parts.

.. |image0| image:: https://travis-ci.org/Koed00/django-q.svg?branch=master
   :target: https://travis-ci.org/Koed00/django-q
.. |q admin| image:: http://i.imgur.com/FBlusZB.png
