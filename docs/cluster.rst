
Cluster
=======
.. py:currentmodule:: django_q

Django Q uses Python's multiprocessing module to manage a pool of workers that will handle your tasks.
Start your cluster using Django's ``manage.py`` command::

    $ python manage.py qcluster


You should see the cluster starting ::

    10:57:40 [Q] INFO Q Cluster-31781 starting.
    10:57:40 [Q] INFO Process-1:1 ready for work at 31784
    10:57:40 [Q] INFO Process-1:2 ready for work at 31785
    10:57:40 [Q] INFO Process-1:3 ready for work at 31786
    10:57:40 [Q] INFO Process-1:4 ready for work at 31787
    10:57:40 [Q] INFO Process-1:5 ready for work at 31788
    10:57:40 [Q] INFO Process-1:6 ready for work at 31789
    10:57:40 [Q] INFO Process-1:7 ready for work at 31790
    10:57:40 [Q] INFO Process-1:8 ready for work at 31791
    10:57:40 [Q] INFO Process-1:9 monitoring at 31792
    10:57:40 [Q] INFO Process-1 guarding cluster at 31783
    10:57:40 [Q] INFO Process-1:10 pushing tasks at 31793
    10:57:40 [Q] INFO Q Cluster-31781 running.


Stopping the cluster with ctrl-c or either the ``SIGTERM`` and ``SIGKILL`` signals, will initiate the :ref:`stop_procedure`::

    16:44:12 [Q] INFO Q Cluster-31781 stopping.
    16:44:12 [Q] INFO Process-1 stopping cluster processes
    16:44:13 [Q] INFO Process-1:10 stopped pushing tasks
    16:44:13 [Q] INFO Process-1:6 stopped doing work
    16:44:13 [Q] INFO Process-1:4 stopped doing work
    16:44:13 [Q] INFO Process-1:1 stopped doing work
    16:44:13 [Q] INFO Process-1:5 stopped doing work
    16:44:13 [Q] INFO Process-1:7 stopped doing work
    16:44:13 [Q] INFO Process-1:3 stopped doing work
    16:44:13 [Q] INFO Process-1:8 stopped doing work
    16:44:13 [Q] INFO Process-1:2 stopped doing work
    16:44:14 [Q] INFO Process-1:9 stopped monitoring results
    16:44:15 [Q] INFO Q Cluster-31781 has stopped.

The number of workers, optional timeouts, recycles and cpu_affinity can be controlled via the :doc:`configure` settings.

Multiple Clusters
-----------------
You can have multiple clusters on multiple machines, working on the same queue as long as:

- They connect to the same :doc:`broker<brokers>`.
- They use the same cluster name. See :doc:`configure`
- They share the same ``SECRET_KEY`` for Django.

Using a Procfile
----------------
If you host on `Heroku <https://heroku.com>`__ or you are using `Honcho <https://github.com/nickstenning/honcho>`__ you can start the cluster from a :file:`Procfile` with an entry like this::

    worker: python manage.py qcluster

Process managers
----------------
While you certainly can run a Django Q with a process manager like `Supervisor <http://supervisord.org/>`__ or `Circus <https://circus.readthedocs.org/en/latest/>`__ it is not strictly necessary.
The cluster has an internal sentinel that checks the health of all the processes and recycles or reincarnates according to your settings or in case of unexpected crashes.
Because of the multiprocessing daemonic nature of the cluster, it is impossible for a process manager to determine the clusters health and resource usage.

An example :file:`circus.ini` ::

    [circus]
    check_delay = 5
    endpoint = tcp://127.0.0.1:5555
    pubsub_endpoint = tcp://127.0.0.1:5556
    stats_endpoint = tcp://127.0.0.1:5557

    [watcher:django_q]
    cmd = python manage.py qcluster
    numprocesses = 1
    copy_env = True

Note that we only start one process. It is not a good idea to run multiple instances of the cluster in the same environment since this does nothing to increase performance and in all likelihood will diminish it.
Control your cluster using the ``workers``, ``recycle`` and ``timeout`` settings in your :doc:`configure`

An example :file:`supervisor.conf` ::

    [program:django-q]
    command = python manage.py qcluster
    stopasgroup = true

Supervisor's ``stopasgroup`` will ensure that the single process doesn't leave orphan process on stop or restart.

Reference
---------

.. py:class:: Cluster

    .. py:method:: start

    Spawns a cluster and then returns

    .. py:method:: stop

    Initiates :ref:`stop_procedure` and waits for it to finish.

    .. py:method:: stat

    returns a :class:`Stat` object with the current cluster status.

    .. py:attribute:: pid

    The cluster process id.

    .. py:attribute:: host

    The current hostname

    .. py:attribute:: sentinel

    returns the :class:`multiprocessing.Process` containing the :ref:`sentinel`.

    .. py:attribute:: timeout

    The clusters timeout setting in seconds

    .. py:attribute:: start_event

    A :class:`multiprocessing.Event` indicating if the :ref:`sentinel` has finished starting the cluster

    .. py:attribute:: stop_event

    A :class:`multiprocessing.Event` used to instruct the :ref:`sentinel` to initiate the :ref:`stop_procedure`

    .. py:attribute:: is_starting

    Bool. Indicating that the cluster is busy starting up

    .. py:attribute:: is_running

    Bool. Tells you if the cluster is up and running.

    .. py:attribute:: is_stopping

    Bool. Shows that the stop procedure has been started.

    .. py:attribute:: has_stopped

    Bool. Tells you if the cluster has finished the stop procedure



