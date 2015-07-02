
Architecture
------------

.. figure:: http://i.imgur.com/wTIeg2T.png
   :alt: Django Q schema


Signed Tasks
""""""""""""

Tasks are first pickled and then signed using Django's own
signing module before being sent to a Redis list. This ensures that task
packages on the Redis server can only be executed and read by clusters
and django servers who share the same secret key.
Optionally the packages can be compressed before transport

Pusher
""""""

The pusher process continuously checks the Redis list for new task
packages and pushes them on the Task Queue.

Worker
""""""

A worker process checks the package signing, unpacks the task, executes
it and saves the return value. Irrespective of the failure or success of
any of these steps, the package is then pushed onto the Result Queue.


Monitor
"""""""

The result monitor checks the Result Queue for processed packages and
saves both failed and successful packages to the Django database.


Sentinel
""""""""

The sentinel spawns all process and then checks the health of all
workers, including the pusher and the monitor. Reincarnating processes
if any may fail. In case of a stop signal, the sentinel will halt the
pusher and instruct the workers and monitor to finish the remaining
items , before exiting. see Stop procedure

Timeouts
""""""""
Before each task execution the worker resets a timer on the sentinel and resets it again after execution.
Meanwhile the the sentinel checks if the timers don't exceed the timeout amount, in which case it will terminate the worker and reincarnate a new one.

Hooks
"""""

Packages can be assigned a hook function, upon completion of the package
this function will be called with the Task object as the first argument.

Stop procedure
""""""""""""""

When a stop signal is given, the sentinel exits the guard loop and instructs the pusher to stop pushing.
Once this is confirmed, the sentinel pushes poison pills onto the task queue and will wait for all the workers to die.
This ensure that the task is emptied before the workers exit. Afterwards the sentinel waits for the monitor to empty the result queue before the stop flow is complete.

