Monitor
=======

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
- **Idle** Everything is ok, but there are no tasks to process.
- **Working** Processing tasks like a good cluster should.
- **Stopping** The cluster does not take on any new tasks and is finishing.
- **Stopped** All tasks have been processed and the cluster is shutting down.

Pool
~~~~

The current number of workers in the cluster pool.

TQ
~~

**Task Queue** counts the number of tasks in the queue

If this keeps rising it means you are taking on more tasks than your cluster can handle.

RQ
~~

**Result Queue** shows the number of results in the queue.

Since results are only saved by a single process which has to access the database.
It's normal for the result queue to take slightly longer to clear than the task queue.

RC
~~

**Reincarnations** shows the amount of processes that have been reincarnated after a sudden death or timeout.
If this number is unusually high, you are either suffering from repeated task errors or severe timeouts and you should check your logs for details.

Up
~~

**Uptime** the amount of time that has passed since the cluster was started.


.. centered:: Press `q` to quit the monitor and return to your terminal.