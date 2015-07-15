Examples
--------

Async emails
============

Sending an email can take a while so why not queue it::

    # Welcome mail with follow up example
    from datetime import timedelta
    from django.utils import timezone
    from django_q import async, schedule, Schedule


    def welcome_mail(user):
        msg = 'Welcome to our website'
        # send this message right away
        async('django.core.mail.send_mail',
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

A good place to use async tasks are Django's model signals. You don't want to delay the saving or creation of objects, but sometimes you want to trigger a lot of actions::

    # Message on object change
    from django.contrib.auth.models import User
    from django.db.models.signals import pre_save
    from django.dispatch import receiver
    from django_q import async

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
                async('tasks.inform_everyone', instance)

The task will send a message to everyone else informing them that the users email address has changed. Note that this adds almost no overhead to the save action::

    # tasks.py
    def inform_everyone(user):
        mails = []
        for u in User.objects.exclude(pk=user.pk):
            msg = 'Dear {}, {} has a new email address: {}'
            msg = msg.format(u.username, user.username, user.email)
            mails.append(('New email', msg,
                          'from@example.com', [u.email]))
        return send_mass_mail(mails)


    # or do it async again
    def inform_everyone_async(user):
        for u in User.objects.exclude(pk=user.pk):
            msg = 'Dear {}, {} has a new email address: {}'
            msg = msg.format(u.username, user.username, user.email)
            async('django.core.mail.send_mail',
                  'New email', msg, 'from@example.com', [u.email])




.. note::

    If you have an example you want to share, please submit a pull request on `github <https://github.com/Koed00/django-q/>`__.



