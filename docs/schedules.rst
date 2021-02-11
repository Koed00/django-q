Schedules
=========
.. py:currentmodule:: django_q

Schedule
--------

Schedules are regular Django models.
You can manage them through the :ref:`admin_page` or directly from your code with the :func:`schedule` function or the :class:`Schedule` model:

.. code:: python

    # Use the schedule wrapper
    from django_q.tasks import schedule

    schedule('math.copysign',
             2, -2,
             hook='hooks.print_result',
             schedule_type='D')

    # Or create the object directly
    from django_q.models import Schedule

    Schedule.objects.create(func='math.copysign',
                            hook='hooks.print_result',
                            args='2,-2',
                            schedule_type=Schedule.DAILY
                            )

    # In case you want to use q_options
    # Specify the broker by using the property broker_name in q_options
    schedule('math.sqrt',
             9,
             hook='hooks.print_result',
             q_options={'timeout': 30, 'broker_name': 'broker_1'},
             schedule_type=Schedule.HOURLY)

    # Run a schedule every 5 minutes, starting at 6 today
    # for 2 hours
    import arrow

    schedule('math.hypot',
             3, 4,
             schedule_type=Schedule.MINUTES,
             minutes=5,
             repeats=24,
             next_run=arrow.utcnow().replace(hour=18, minute=0))

    # Use a cron expression
    schedule('math.hypot',
             3, 4,
             schedule_type=Schedule.CRON,
             cron = '0 22 * * 1-5')



Missed schedules
----------------
If your cluster has not run for a while, the default behavior for the scheduler is to play catch up with the schedules and keep executing them until they are up to date.
In practical terms this means the scheduler will execute tasks in the past, reschedule them in the past and immediately execute them again until the schedule is set in the future.
This default behavior is intended to facilitate schedules that poll or gather statistics, but might not be suitable to your particular situation.
You can change this by setting the :ref:`catch_up` configuration setting to ``False``.
The scheduler will then skip execution of scheduled events in the past.
Instead those tasks will run once when the cluster starts again and the scheduler will find the next available slot in the future according to original schedule parameters.

Management Commands
-------------------

If you want to schedule regular Django management commands, you can use the :mod:`django.core.management` module to call them directly:

.. code-block:: python

    from django_q.tasks import schedule

    # run `manage.py clearsession` every hour
    schedule('django.core.management.call_command',
             'clearsessions',
             schedule_type='H')

Or you can make a wrapper function which you can then schedule in Django Q:

.. code-block:: python

    # tasks.py
    from django.core import management

    # wrapping `manage.py clearsessions`
    def clear_sessions_command():
        return management.call_command('clearsessions')

    # now you can schedule it to run every hour
    from django_q.tasks import schedule

    schedule('tasks.clear_sessions_command', schedule_type='H')


Check out the :ref:`shell` examples if you want to schedule regular shell commands

.. note::

   Schedules needs the optional :ref:`Croniter<croniter_package>` package installed to parse cron expressions.

Reference
---------

..  py:function:: schedule(func, *args, name=None, hook=None, schedule_type='O', minutes=None, repeats=-1, next_run=now() , q_options=None, **kwargs)

    Creates a schedule

    :param str func: the function to schedule. Dotted strings only.
    :param args: arguments for the scheduled function.
    :param str name: An optional name for your schedule.
    :param str hook: optional result hook function. Dotted strings only.
    :param str schedule_type: (O)nce, M(I)nutes, (H)ourly, (D)aily, (W)eekly, (M)onthly, (Q)uarterly, (Y)early or (C)ron :attr:`Schedule.TYPE`
    :param int minutes: Number of minutes for the Minutes type.
    :param str cron: Cron expression for the Cron type.
    :param int repeats: Number of times to repeat schedule. -1=Always, 0=Never, n =n.
    :param datetime next_run: Next or first scheduled execution datetime.
    :param dict q_options: options passed to async_task for this schedule
    :param kwargs: optional keyword arguments for the scheduled function.
    
    .. note::

        q_options does not accept the 'broker' key with a broker instance but accepts a 'broker_name' key instead. This can be used to specify the broker connection name to assign the task. If a broker with the specified name does not exist or is not running at the moment of placing the task in queue it fallbacks to the random broker/queue that handled the schedule.


.. class:: Schedule

    A database model for task schedules.

    .. py:attribute:: id

    Primary key

    .. py:attribute:: name

    A name for your schedule. Tasks created by this schedule will assume this or the primary key as their group id.

    .. py:attribute:: func

    The function to be scheduled

    .. py:attribute:: hook

    Optional hook function to be called after execution.

    .. py:attribute:: args

    Positional arguments for the function.

    .. py:attribute:: kwargs

    Keyword arguments for the function

    .. py:attribute:: schedule_type

    The type of schedule. Follows :attr:`Schedule.TYPE`

    .. py:attribute:: TYPE

    :attr:`ONCE`, :attr:`MINUTES`, :attr:`HOURLY`, :attr:`DAILY`, :attr:`WEEKLY`, :attr:`MONTHLY`, :attr:`QUARTERLY`, :attr:`YEARLY`, :attr:`CRON`


    .. py:attribute:: minutes

    The number of minutes the :attr:`MINUTES` schedule should use.
    Is ignored for other schedule types.

    .. py:attribute:: cron

    A cron string describing the schedule. You need the optional `croniter` package installed for this.

    .. py:attribute:: repeats

    Number of times to repeat the schedule. -1=Always, 0=Never, n =n.
    When set to -1, this will keep counting down.

    .. py:attribute:: next_run

    Datetime of the next scheduled execution.

    .. py:attribute:: task

    Id of the last task generated by this schedule.

    .. py:method:: last_run()

    Admin link to the last executed task.

    .. py:method:: success()

    Returns the success status of the last executed task.

    .. py:attribute:: ONCE

    `'O'` the schedule will only run once.
    If it has a negative :attr:`repeats` it will be deleted after it has run.
    If you want to keep the result, set :attr:`repeats` to a positive number.

    .. py:attribute:: MINUTES

    `'I'` will run every :attr:`minutes` after its first run.

    .. py:attribute:: HOURLY

    `'H'` the scheduled task will run every hour after its first run.

    .. py:attribute:: DAILY

    `'D'` the scheduled task will run every day at the time of its first run.

    .. py:attribute:: WEEKLY

    `'W'` the task will run every week on they day and time of the first run.

    .. py:attribute:: MONTHLY

    `'M'` the tasks runs every month on they day and time of the last run.

    .. note::

        Months are tricky. If you schedule something on the 31st of the month and the next month has only 30 days or less, the task will run on the last day of the next month.
        It will however continue to run on that day, e.g. the 28th, in subsequent months.

    .. py:attribute:: QUARTERLY

    `'Q'` this task runs once every 3 months on the day and time of the last run.

    .. py:attribute:: YEARLY

    `'Y'` only runs once a year. The same caution as with months apply;
    If you set this to february 29th, it will run on february 28th in the following years.

    .. py:attribute:: CRON

    `'C'` uses the optional `croniter` package to determine a schedule based on a cron expression.


