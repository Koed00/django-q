.. _admin_page:

Admin pages
===========

Django Q does not use custom HTML pages, but instead uses what is offered by Django's model admin by default.
When you open Django Q's admin pages you will see three models:

Successful tasks
----------------

Shows all successfully executed tasks. Meaning they did not encounter any errors during execution.
From here you can look at details of each task or delete them.

Uses the :class:`Success` proxy model.

.. tip::

    The maximum number of successful tasks can be set using the `save_limit` :ref:`configuration` option.



Failed tasks
------------
Failed tasks have encountered an error, preventing them from finishing execution.
The worker will try to put the error in the `result` field of the task so you can review what happened.

You can resubmit a failed task back to the queue using the admins action menu.

Uses the :class:`Failure` proxy model

Scheduled tasks
---------------

Here you can check on the status of your scheduled tasks, create, edit or delete them.

Repeats
~~~~~~~
If you want a schedule to only run a finite amount of times, e.g. every hour for the next 24 hours, you can do that using the :attr:`Schedule.repeats` attribute.
In this case you would set the schedule type to :attr:`Schedule.HOURLY` and the repeats to `24`. Every time the schedule runs the repeats count down until it hits zero and schedule is no longer run.

When you set repeats to `-1` the schedule will continue indefinitely and the repeats will still count down. This can be used as an indicator of how many times the schedule has been executed.

An exception to this are schedules of type :attr:`Schedule.ONCE`. Repeats are ignored by this schedule type and it will always reset it zero after execution.

.. note::

    To run a `Once` schedule again, change the repeats to something other than `0`. Set a new run time before you do this or let it execute immediately.

Next run
~~~~~~~~

Shows you when this task will be added to the queue next.


Last run
~~~~~~~~

Links to the task result of the last scheduled run. Shows nothing if the schedule hasn't run yet or if task result has been deleted.

Success
~~~~~~~

Indicates the success status of the last scheduled task, if any.


Uses the :class:`Schedule` model
