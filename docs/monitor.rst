Monitor
=======
.. py:currentmodule::django_q.monitor

The cluster monitor shows information about all the Q clusters connected to your project.

Start the monitor with Django's `manage.py` command::

    $ python manage.py qmonitor


.. image:: _static/monitor.png

Legend
------

Host
~~~~

Shows the hostname of the server this cluster is running on.

Id
~~

The cluster Id. Same as the cluster process ID or pid.

State
~~~~~

Current state of the cluster:

- **Starting** The cluster is spawning workers and getting ready.
- **Idle** Everything is ok, but there are no tasks to process. [#f1]_
- **Working** Processing tasks like a good cluster should.
- **Stopping** The cluster does not take on any new tasks and is finishing.
- **Stopped** All tasks have been processed and the cluster is shutting down.

Pool
~~~~

The current number of workers in the cluster pool.

TQ
~~

**Task Queue** counts the number of tasks in the queue [#f1]_

If this keeps rising it means you are taking on more tasks than your cluster can handle.
You can limit this by settings the :ref:`queue_limit` in your cluster configuration, after which it will turn green when that limit has been reached.
If your task queue is always hitting its limit and your running out of resources, it may be time to add another cluster.

RQ
~~

**Result Queue** shows the number of results in the queue. [#f1]_

Since results are only saved by a single process which has to access the database.
It's normal for the result queue to take slightly longer to clear than the task queue.

RC
~~

**Reincarnations** shows the amount of processes that have been reincarnated after a recycle, sudden death or timeout.
If this number is unusually high, you are either suffering from repeated task errors or severe timeouts and you should check your logs for details.

Up
~~

**Uptime** the amount of time that has passed since the cluster was started.


.. centered:: Press `q` to quit the monitor and return to your terminal.


Status
------

You can check the status of your clusters straight from your code with :class:`Stat`:

.. code:: python

    from django_q.monitor import Stat

    for stat in Stat.get_all():
        print(stat.cluster_id, stat.status)

    # or if you know the cluster id
    cluster_id = 1234
    stat = Stat.get(cluster_id)
    print(stat.status, stat.workers)

Reference
---------

.. py:class:: Stat

   Cluster status object.

    .. py:attribute:: cluster_id

    Id of this cluster. Corresponds with the process id.

    .. py:attribute:: tob

    Time Of Birth

    .. py:method:: uptime

    Shows the number of seconds passed since the time of birth

    .. py:attribute:: reincarnations

    The number of times the sentinel had to start a new worker process.

    .. py:attribute:: status

    String representing the current cluster status.

    .. py:attribute:: task_q_size

    The number of tasks currently in the task queue. [#f1]_

    .. py:attribute:: done_q_size

    The number of tasks currently in the result queue. [#f1]_

    .. py:attribute:: pusher

    The pid of the pusher process

    .. py:attribute:: monitor

    The pid of the monitor process

    .. py:attribute:: sentinel

    The pid of the sentinel process

    .. py:attribute:: workers

    A list of process ids of the workers currently in the cluster pool.

    .. py:method:: empty_queues

    Returns true or false depending on any tasks still present in the task or result queue.

    .. py:classmethod:: get(cluster_id, r=redis_client)

    Gets the current :class:`Stat` for the cluster id. Takes an optional redis connection.

    .. py:classmethod:: get_all(r=redis_client)

    Returns a list of :class:`Stat` objects for all active clusters. Takes an optional redis connection.

.. rubric:: Footnotes

.. [#f1] Uses :meth:`multiprocessing.Queue.qsize()` which is not implemented on OS X.
