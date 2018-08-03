.. py:currentmodule:: django_q

Groups
======
You can group together results by passing :func:`async_task` the optional ``group`` keyword:

.. code-block:: python

    # result group example
    from django_q.tasks import async_task, result_group

    for i in range(4):
        async_task('math.modf', i, group='modf')

    # wait until the group has 4 results
    result = result_group('modf', count=4)
    print(result)

.. code-block:: python

    [(0.0, 0.0), (0.0, 1.0), (0.0, 2.0), (0.0, 3.0)]

Note that this particular example can be achieved much faster with :doc:`iterable`

Take care to not limit your results database too much and call :func:`delete_group` before each run, unless you want your results to keep adding up.
Instead of :func:`result_group` you can also use :func:`fetch_group` to return a queryset of :class:`Task` objects.:

.. code-block:: python

    # fetch group example
    from django_q.tasks import fetch_group, count_group, result_group

    # count the number of failures
    failure_count = count_group('modf', failures=True)

    # only use the successes
    results = fetch_group('modf')
    if failure_count:
        results = results.exclude(success=False)
    results =  [task.result for task in successes]

    # this is the same as
    results = fetch_group('modf', failures=False)
    results =  [task.result for task in successes]

    # and the same as
    results = result_group('modf') # filters failures by default


Getting results by using :func:`result_group` is of course much faster than using :func:`fetch_group`, but it doesn't offer the benefits of Django's queryset functions.

.. note::

   Calling ``Queryset.values`` for the result on Django 1.7 or lower will return a list of encoded results.
   If you can't upgrade to Django 1.8, use list comprehension or an iterator to return decoded results.

You can also access group functions from a task result instance:

.. code-block:: python

    from django_q.tasks import fetch

    task = fetch('winter-speaker-alpha-ceiling')
    if  task.group_count() > 100:
        print(task.group_result())
        task.group_delete()
        print('Deleted group {}'.format(task.group))

or call them directly on :class:`AsyncTask` object:

.. code-block:: python

    from django_q.tasks import AsyncTask

    # add a task to the math group and run it cached
    a = AsyncTask('math.floor', 2.5, group='math', cached=True)

    # wait until this tasks group has 10 results
    result = a.result_group(count=10)

Reference
---------
.. py:function:: result_group(group_id, failures=False, wait=0, count=None, cached=False)

    Returns the results of a task group

    :param str group_id: the group identifier
    :param bool failures: set this to ``True`` to include failed results
    :param int wait: optional milliseconds to wait for a result or count. -1 for indefinite
    :param int count: block until there are this many results in the group
    :param bool cached: run this against the cache backend
    :returns: a list of results
    :rtype: list

.. py:function:: fetch_group(group_id, failures=True, wait=0, count=None, cached=False)

    Returns a list of tasks in a group

    :param str group_id: the group identifier
    :param bool failures: set this to ``False`` to exclude failed tasks
    :param int wait: optional milliseconds to wait for a task or count. -1 for indefinite
    :param int count: block until there are this many tasks in the group
    :param bool cached: run this against the cache backend.
    :returns: a list of :class:`Task`
    :rtype: list

.. py:function:: count_group(group_id, failures=False, cached=False)

    Counts the number of task results in a group.

    :param str group_id: the group identifier
    :param bool failures: counts the number of failures if ``True``
    :param bool cached: run this against the cache backend.
    :returns: the number of tasks or failures in a group
    :rtype: int

.. py:function:: delete_group(group_id, tasks=False, cached=False)

    Deletes a group label from the database.

    :param str group_id: the group identifier
    :param bool tasks: also deletes the associated tasks if ``True``
    :param bool cached: run this against the cache backend.
    :returns: the numbers of tasks affected
    :rtype: int
