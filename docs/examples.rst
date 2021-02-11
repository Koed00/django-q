Examples
--------
.. py:currentmodule:: django_q

Emails
======

Sending an email can take a while so why not queue it:

.. code-block:: python

    # Welcome mail with follow up example
    from datetime import timedelta
    from django.utils import timezone
    from django_q.tasks import async_task, schedule
    from django_q.models import Schedule


    def welcome_mail(user):
        msg = 'Welcome to our website'
        # send this message right away
        async_task('django.core.mail.send_mail',
                'Welcome',
                msg,
                'from@example.com',
                [user.email])
        # and this follow up email in one hour
        msg = 'Here are some tips to get you started...'
        schedule('django.core.mail.send_mail',
                 'Follow up',
                 msg,
                 'from@example.com',
                 [user.email],
                 schedule_type=Schedule.ONCE,
                 next_run=timezone.now() + timedelta(hours=1))

        # since the `repeats` defaults to -1
        # this schedule will erase itself after having run


Since you're only telling Django Q to take care of the emails, you can quickly move on to serving web pages to your user.

Signals
=======

A good place to use async tasks are Django's model signals. You don't want to delay the saving or creation of objects, but sometimes you want to trigger a lot of actions:

.. code-block:: python

    # Message on object change
    from django.contrib.auth.models import User
    from django.db.models.signals import pre_save
    from django.dispatch import receiver
    from django_q.tasks import async_task

    # set up the pre_save signal for our user
    @receiver(pre_save, sender=User)
    def email_changed(sender, instance, **kwargs):
        try:
            user = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            pass  # new user
        else:
            # has his email changed?
            if not user.email == instance.email:
                # tell everyone
                async_task('tasks.inform_everyone', instance)

The task will send a message to everyone else informing them that the users email address has changed. Note that this adds almost no overhead to the save action:

.. code-block:: python

    # tasks.py
    def inform_everyone(user):
        mails = []
        for u in User.objects.exclude(pk=user.pk):
            msg = f"Dear {u.username}, {user.username} has a new email address: {user.email}"
            mails.append(('New email', msg,
                          'from@example.com', [u.email]))
        return send_mass_mail(mails)

.. code-block:: python

    # or do it async again
    def inform_everyone_async(user):
        for u in User.objects.exclude(pk=user.pk):
            msg = f"Dear {u.username}, {user.username} has a new email address: {user.email}"
            async_task('django.core.mail.send_mail',
                    'New email', msg, 'from@example.com', [u.email])


Of course you can do other things beside sending emails. These are just generic examples. You can use signals with async to update fields in other objects too.
Let's say this users email address is not just on the User object, but you stored it in some other places too without a reference.
By attaching an async action to the save signal, you can now update that email address in those other places without impacting the the time it takes to return your views.


Reports
=======

In this example the user requests a report and we let the cluster do the generating, while handling the result with a hook.

.. code-block:: python

    # Report generation with hook example
    from django_q.tasks import async_task

    # views.py
    # user requests a report.
    def create_report(request):
        async_task('tasks.create_html_report',
                request.user,
                hook='tasks.email_report')

.. code-block:: python

    # tasks.py
    from django_q.tasks import async_task

    # report generator
    def create_html_report(user):
        html_report = 'We had a great quarter!'
        return html_report

    # report mailer
    def email_report(task):
        if task.success:
            # Email the report
            async_task('django.core.mail.send_mail',
                    'The report you requested',
                    task.result,
                    'from@example.com',
                    task.args[0].email)
        else:
            # Tell the admins something went wrong
            async_task('django.core.mail.mail_admins',
                    'Report generation failed',
                    task.result)


The hook is practical here, because it allows us to detach the sending task from the report generation function and to report on possible failures.

Haystack
========
If you use `Haystack <http://haystacksearch.org/>`__ as your projects search engine,
here's an example of how you can have Django Q take care of your indexes in real time using model signals:

.. code-block:: python

    # Real time Haystack indexing
    from .models import Document
    from django.db.models.signals import post_save
    from django.dispatch import receiver
    from django_q.tasks import async_task

    # hook up the post save handler
    @receiver(post_save, sender=Document)
    def document_changed(sender, instance, **kwargs):
        async_task('tasks.index_object', sender, instance, save=False)
        # turn off result saving to not flood your database

.. code-block:: python

    # tasks.py
    from haystack import connection_router, connections

    def index_object(sender, instance):
        # get possible backends
        backends = connection_router.for_write(instance=instance)

        for backend in backends:
            # get the index for this model
            index = connections[backend].get_unified_index()\
                .get_index(sender)
            # update it
            index.update_object(instance, using=backend)

Now every time a Document is saved, your indexes will be updated without causing a delay in your save action.
You could expand this to dealing with deletes, by adding a ``post_delete`` signal and calling ``index.remove_object`` in the async_task function.

.. _shell:

Shell
=====
You can execute or schedule shell commands using Pythons :mod:`subprocess` module:

.. code-block:: python

    from django_q.tasks import async_task, result

    # make a backup copy of setup.py
    async_task('subprocess.call', ['cp', 'setup.py', 'setup.py.bak'])

    # call ls -l and dump the output
    task_id=async_task('subprocess.check_output', ['ls', '-l'])

    # get the result
    dir_list = result(task_id)

In Python 3.5 the subprocess module has changed quite a bit and returns a :class:`subprocess.CompletedProcess` object instead:

.. code-block:: python

    from django_q.tasks import async_task, result

    # make a backup copy of setup.py
    tid = async_task('subprocess.run', ['cp', 'setup.py', 'setup.py.bak'])

    # get the result
    r=result(tid, 500)
    # we can now look at the original arguments
    >>> r.args
    ['cp', 'setup.py', 'setup.py.bak']
    # and the returncode
    >>> r.returncode
    0

    # to capture the output we'll need a pipe
    from subprocess import PIPE

    # call ls -l and pipe the output
    tid = async_task('subprocess.run', ['ls', '-l'], stdout=PIPE)
    # get the result
    res = result(tid, 500)
    # print the output
    print(res.stdout)


Instead of :func:`async_task` you can of course also use :func:`schedule` to schedule commands.

For regular Django management commands, it is easier to call them directly:

.. code-block:: python

    from django_q.tasks import async_task, schedule

    async_task('django.core.management.call_command','clearsessions')

    # or clear those sessions every hour

    schedule('django.core.management.call_command',
         'clearsessions',
         schedule_type='H')



Groups
======
A group example with Kernel density estimation for probability density functions using the Parzen-window technique.
Adapted from `Sebastian Raschka's blog <http://sebastianraschka.com/Articles/2014_multiprocessing_intro.html>`__

.. code-block:: python

    # Group example with Parzen-window estimation
    import numpy

    from django_q.tasks import async_task, result_group, delete_group

    # the estimation function
    def parzen_estimation(x_samples, point_x, h):
        k_n = 0
        for row in x_samples:
            x_i = (point_x - row[:, numpy.newaxis]) / h
            for row in x_i:
                if numpy.abs(row) > (1 / 2):
                    break
            else:
                k_n += 1
        return h, (k_n / len(x_samples)) / (h ** point_x.shape[1])

    # create 100 calculations and return the collated result
    def parzen_async():
        # clear the previous results
        delete_group('parzen', cached=True)
        mu_vec = numpy.array([0, 0])
        cov_mat = numpy.array([[1, 0], [0, 1]])
        sample = numpy.random. \
            multivariate_normal(mu_vec, cov_mat, 10000)
        widths = numpy.linspace(1.0, 1.2, 100)
        x = numpy.array([[0], [0]])
        # async_task them with a group label to the cache backend
        for w in widths:
            async_task(parzen_estimation, sample, x, w,
                    group='parzen', cached=True)
        # return after 100 results
        return result_group('parzen', count=100, cached=True)



Django Q is not optimized for distributed computing, but this example will give you an idea of what you can do with task :doc:`group`.

Alternatively the ``parzen_async()`` function can also be written with :func:`async_iter`, which automatically utilizes the cache backend and groups to return a single result from an iterable:

.. code-block:: python

    # create 100 calculations and return the collated result
    def parzen_async():
        mu_vec = numpy.array([0, 0])
        cov_mat = numpy.array([[1, 0], [0, 1]])
        sample = numpy.random. \
            multivariate_normal(mu_vec, cov_mat, 10000)
        widths = numpy.linspace(1.0, 1.2, 100)
        x = numpy.array([[0], [0]])
        # async_task them with async_task iterable
        args = [(sample, x, w) for w in widths]
        result_id = async_iter(parzen_estimation, args, cached=True)
        # return the cached result or timeout after 10 seconds
        return result(result_id, wait=10000, cached=True)



Http Health Check
=================
An example of a python http server you can use (localhost:8080) to validate the health status of all the clusters in your environment.  Example is http only.

Requires cache to be enabled. Save file in your Django project's root directory and run with command: ``python worker_hc.py`` in your container or other environment.  Can be customized to show whatever you'd like from the Stat class or modified as needed.

.. code-block:: python

    from http.server import BaseHTTPRequestHandler, HTTPServer
    from mtt_app.settings.base import EMAIL_USE_TLS

    import os
    import django

    #  Set the correct path to you settings module
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my.settings.path")

    # All django stuff has to come after the setup:
    django.setup()

    from django_q.monitor import Stat
    from django_q.conf import Conf

    # Set host and port settings
    hostName = "localhost"
    serverPort = 8080


    class HealthCheckServer(BaseHTTPRequestHandler):
        def do_GET(self):
            
            # Count the clusters and their status
            happy_clusters = 0
            total_clusters = 0

            for stat in Stat.get_all():
                total_clusters += 1
                if stat.status in [Conf.IDLE, Conf.WORKING]:
                    happy_clusters += 1

            # Return 200 response if there is at least 1 cluster running,
            # and make sure all running clusters are happy
            if total_clusters and happy_clusters == total_clusters:
                response_code = 200
            else:
                response_code = 500

            self.send_response(response_code)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            self.wfile.write(
                bytes("<html><head><title>Django-Q Heath Check</title></head>", "utf-8")
            )
            self.wfile.write(
                bytes(f"<p>Health check returned {response_code} response</p>", "utf-8")
            )
            self.wfile.write(
                bytes(
                    f"<p>{happy_clusters} of {total_clusters} cluster(s) are happy</p></html>",
                    "utf-8",
                )
            )


    if __name__ == "__main__":
        webServer = HTTPServer((hostName, serverPort), HealthCheckServer)
        print("Server started at http://%s:%s" % (hostName, serverPort))

        try:
            webServer.serve_forever()
        except KeyboardInterrupt:
            pass

        webServer.server_close()
        print("Server stopped.")
        
        
        
.. note::

    If you have an example you want to share, please submit a pull request on `github <https://github.com/Koed00/django-q/>`__.



