Schedules
=========

Schedules are regular Django models. You can manage them through the :ref:`admin_page` or directly from your code with the :func:`schedule` function or the :class:`Schedule` model:

.. code:: python

    from django_q import Schedule, schedule

    # Use the schedule wrapper

    schedule('math.copysign',
             2, -2,
             hook='hooks.print_result',
             schedule_type=Schedule.DAILY)

    # Or create the object directly

    Schedule.objects.create(func='math.copysign',
                            hook='hooks.print_result',
                            args='2,-2',
                            schedule_type=Schedule.DAILY
                            )


.. py:function:: schedule(func, *args, hook=None, schedule_type='O', repeats=-1, next_run=now() , **kwargs)

    Creates a schedule

    :param str func: the function to schedule. Dotted strings only.
    :param args: arguments for the scheduled function.
    :param str hook: optional result hook function. Dotted strings only.
    :param str schedule_type: (O)nce, (H)ourly, (D)aily, (W)eekly, (M)onthly, (Q)uarterly, (Y)early
    :param int repeats: Number of times to repeat schedule. `-1`=Always, `0`=Never, `n` =n.
    :param datetime next_run: Next or first scheduled execution datetime.
    :param kwargs: optional keyword arguments for the scheduled function.

.. py:class:: Schedule

