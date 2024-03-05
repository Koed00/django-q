
Cluster
=======
.. py:currentmodule:: django_q

Django Q2 uses Python's multiprocessing module to manage a pool of workers that will handle your tasks.
Start your cluster using Django's ``manage.py`` command::

    $ python manage.py qcluster


You should see the cluster starting ::

    10:57:40 [Q] INFO Q Cluster freddie-uncle-twenty-ten starting.
    10:57:40 [Q] INFO Process-ede257774c4444c980ab479f10947acc ready for work at 31784
    10:57:40 [Q] INFO Process-ed580482da3f42968230baa2e4253e42 ready for work at 31785
    10:57:40 [Q] INFO Process-8a370dc2bc1d49aa9864e517c9895f74 ready for work at 31786
    10:57:40 [Q] INFO Process-74912f9844264d1397c6e54476b530c0 ready for work at 31787
    10:57:40 [Q] INFO Process-b00edb26c6074a6189e5696c60aeb35b ready for work at 31788
    10:57:40 [Q] INFO Process-b0862965db04479f9784a26639ee51e0 ready for work at 31789
    10:57:40 [Q] INFO Process-7e8abbb8ca2d4d9bb20a937dd5e2872b ready for work at 31790
    10:57:40 [Q] INFO Process-b0862965db04479f9784a26639ee51e0 ready for work at 31791
    10:57:40 [Q] INFO Process-67fa9461ac034736a766cd813f617e62 monitoring at 31792
    10:57:40 [Q] INFO Process-eac052c646b2459797cee98bdb84c85d guarding cluster at 31783
    10:57:40 [Q] INFO Process-5d98deb19b1e4b2da2ef1e5bd6824f75 pushing tasks at 31793
    10:57:40 [Q] INFO Q Cluster freddie-uncle-twenty-ten running.


Stopping the cluster with ctrl-c or either the ``SIGTERM`` and ``SIGKILL`` signals, will initiate the :ref:`stop_procedure`::

    16:44:12 [Q] INFO Q Cluster freddie-uncle-twenty-ten stopping.
    16:44:12 [Q] INFO Process-eac052c646b2459797cee98bdb84c85d stopping cluster processes
    16:44:13 [Q] INFO Process-5d98deb19b1e4b2da2ef1e5bd6824f75 stopped pushing tasks
    16:44:13 [Q] INFO Process-b0862965db04479f9784a26639ee51e0 stopped doing work
    16:44:13 [Q] INFO Process-7e8abbb8ca2d4d9bb20a937dd5e2872b stopped doing work
    16:44:13 [Q] INFO Process-b0862965db04479f9784a26639ee51e0 stopped doing work
    16:44:13 [Q] INFO Process-b00edb26c6074a6189e5696c60aeb35b stopped doing work
    16:44:13 [Q] INFO Process-74912f9844264d1397c6e54476b530c0 stopped doing work
    16:44:13 [Q] INFO Process-8a370dc2bc1d49aa9864e517c9895f74 stopped doing work
    16:44:13 [Q] INFO Process-ed580482da3f42968230baa2e4253e42 stopped doing work
    16:44:13 [Q] INFO Process-ede257774c4444c980ab479f10947acc stopped doing work
    16:44:14 [Q] INFO Process-67fa9461ac034736a766cd813f617e62 stopped monitoring results
    16:44:15 [Q] INFO Q Cluster freddie-uncle-twenty-ten has stopped.

The number of workers, optional timeouts, recycles and cpu_affinity can be controlled via the :doc:`configure` settings.

Multiple Clusters
-----------------
You can have multiple clusters on multiple machines, working on the same queue as long as:

- They connect to the same :doc:`broker<brokers>`.
- They use the same cluster name. See :doc:`configure`
- They share the same ``SECRET_KEY`` for Django.

.. _multiple-queues

Multiple Queues
-----------------
You can have multiple queues in one Django site, and use multiple cluster to work on each queue.
Different queues are identified by different queue names which are also cluster names.
To run an alternate cluster, e.g. to work on the 'long' queue, start your cluster with command::

    # On Linux
    $ Q_CLUSTER_NAME=long python manage.py qcluster

    # On Windows
    $ python manage.py qcluster --name long

You can set different Q_CLUSTER options for alternative clusters, such as 'timeout', 'queue_limit'
and any other options which are valid in :doc:`configure`. See :ref:`alt-clusters`.

.. note::

    To use multiple queue, use the keyword argument `cluster` in async_task() and schedule():

    * if `cluster` is not set (the default), async_task() and schedule() will be handled by the default cluster;
    * if `cluster` is set, only clusters with matching cluster name will run the task or do the schedule.

Using a Procfile
----------------
If you host on `Heroku <https://heroku.com>`__ or you are using `Honcho <https://github.com/nickstenning/honcho>`__ you can start the cluster from a :file:`Procfile` with an entry like this::

    worker: python manage.py qcluster

Process managers
----------------
While you certainly can run a Django Q2 with a process manager like `Supervisor <http://supervisord.org/>`__ or `Circus <https://circus.readthedocs.org/en/latest/>`__ it is not strictly necessary.
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



