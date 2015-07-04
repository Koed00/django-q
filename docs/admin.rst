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

    The maximum number of succesful tasks can be set using the `save_limit` :ref:`configuration` option.



Failed tasks
------------
Failed tasks have encountered an error, preventing them from finishing execution.
The worker will try to put the error in the `result` field of the task so you can review what happened.

You can resubmit a failed task back to the queue using the admins action menu.

Uses the :class:`Failure` proxy model

Scheduled tasks
---------------


Uses the :class:`Schedule` model
