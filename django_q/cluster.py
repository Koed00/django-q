# Standard
import ast
import pydoc
import signal
import socket
import traceback
import uuid
from datetime import datetime, timedelta
from multiprocessing import Event, Process, Value, current_process
from time import sleep

# Django
from django import core, db
from django.apps.registry import apps

try:
    apps.check_apps_ready()
except core.exceptions.AppRegistryNotReady:
    import django

    django.setup()

from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Local
import django_q.tasks
from django_q.brokers import Broker, get_broker
from django_q.conf import (
    Conf,
    croniter,
    error_reporter,
    get_ppid,
    logger,
    psutil,
    resource,
)
from django_q.humanhash import humanize
from django_q.models import Schedule, Success, Task
from django_q.queues import Queue
from django_q.signals import post_execute, pre_execute
from django_q.signing import BadSignature, SignedPackage
from django_q.status import Stat, Status

from .utils import get_func_repr, localtime


class Cluster:
    def __init__(self, broker: Broker = None):
        self.broker = broker or get_broker()
        self.sentinel = None
        self.stop_event = None
        self.start_event = None
        self.pid = current_process().pid
        self.cluster_id = uuid.uuid4()
        self.host = socket.gethostname()
        self.timeout = Conf.TIMEOUT
        signal.signal(signal.SIGTERM, self.sig_handler)
        signal.signal(signal.SIGINT, self.sig_handler)

    def start(self) -> int:
        # Start Sentinel
        self.stop_event = Event()
        self.start_event = Event()
        self.sentinel = Process(
            target=Sentinel,
            args=(
                self.stop_event,
                self.start_event,
                self.cluster_id,
                self.broker,
                self.timeout,
            ),
        )
        self.sentinel.start()
        logger.info(_("Q Cluster %(name)s starting.") % {"name": self.name})
        while not self.start_event.is_set():
            sleep(0.1)
        return self.pid

    def stop(self) -> bool:
        if not self.sentinel.is_alive():
            return False
        logger.info(_("Q Cluster %(name)s stopping.") % {"name": self.name})
        self.stop_event.set()
        self.sentinel.join()
        logger.info(_("Q Cluster %(name)s has stopped.") % {"name": self.name})
        self.start_event = None
        self.stop_event = None
        return True

    def sig_handler(self, signum, frame):
        logger.debug(
            _("%(name)s got signal %(signal)s")
            % {
                "name": current_process().name,
                "signal": Conf.SIGNAL_NAMES.get(signum, "UNKNOWN"),
            }
        )
        self.stop()

    @property
    def stat(self) -> Status:
        if self.sentinel:
            return Stat.get(pid=self.pid, cluster_id=self.cluster_id)
        return Status(pid=self.pid, cluster_id=self.cluster_id)

    @property
    def name(self) -> str:
        return humanize(self.cluster_id.hex)

    @property
    def is_starting(self) -> bool:
        return self.stop_event and self.start_event and not self.start_event.is_set()

    @property
    def is_running(self) -> bool:
        return self.stop_event and self.start_event and self.start_event.is_set()

    @property
    def is_stopping(self) -> bool:
        return (
            self.stop_event
            and self.start_event
            and self.start_event.is_set()
            and self.stop_event.is_set()
        )

    @property
    def has_stopped(self) -> bool:
        return self.start_event is None and self.stop_event is None and self.sentinel


class Sentinel:
    def __init__(
        self,
        stop_event,
        start_event,
        cluster_id,
        broker=None,
        timeout=Conf.TIMEOUT,
        start=True,
    ):
        # Make sure we catch signals for the pool
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        self.pid = current_process().pid
        self.cluster_id = cluster_id
        self.parent_pid = get_ppid()
        self.name = current_process().name
        self.broker = broker or get_broker()
        self.reincarnations = 0
        self.tob = timezone.now()
        self.stop_event = stop_event
        self.start_event = start_event
        self.pool_size = Conf.WORKERS
        self.pool = []
        self.timeout = timeout
        self.task_queue = (
            Queue(maxsize=Conf.QUEUE_LIMIT) if Conf.QUEUE_LIMIT else Queue()
        )
        self.result_queue = Queue()
        self.event_out = Event()
        self.monitor = None
        self.pusher = None
        if start:
            self.start()

    def start(self):
        self.broker.ping()
        self.spawn_cluster()
        self.guard()

    def status(self) -> str:
        if not self.start_event.is_set() and not self.stop_event.is_set():
            return Conf.STARTING
        elif self.start_event.is_set() and not self.stop_event.is_set():
            if self.result_queue.empty() and self.task_queue.empty():
                return Conf.IDLE
            return Conf.WORKING
        elif self.stop_event.is_set() and self.start_event.is_set():
            if self.monitor.is_alive() or self.pusher.is_alive() or len(self.pool) > 0:
                return Conf.STOPPING
            return Conf.STOPPED

    def spawn_process(self, target, *args) -> Process:
        """
        :type target: function or class
        """
        p = Process(target=target, args=args)
        p.daemon = True
        if target == worker:
            p.daemon = Conf.DAEMONIZE_WORKERS
            p.timer = args[2]
            self.pool.append(p)
        p.start()
        return p

    def spawn_pusher(self) -> Process:
        return self.spawn_process(pusher, self.task_queue, self.event_out, self.broker)

    def spawn_worker(self):
        self.spawn_process(
            worker, self.task_queue, self.result_queue, Value("f", -1), self.timeout
        )

    def spawn_monitor(self) -> Process:
        return self.spawn_process(monitor, self.result_queue, self.broker)

    def reincarnate(self, process):
        """
        :param process: the process to reincarnate
        :type process: Process or None
        """
        # close connections before spawning new process
        if not Conf.SYNC:
            db.connections.close_all()
        if process == self.monitor:
            self.monitor = self.spawn_monitor()
            logger.error(
                _("reincarnated monitor %(name)s after sudden death")
                % {"name": process.name}
            )
        elif process == self.pusher:
            self.pusher = self.spawn_pusher()
            logger.error(
                _("reincarnated pusher %(name)s after sudden death")
                % {"name": process.name}
            )
        else:
            self.pool.remove(process)
            self.spawn_worker()
            if process.timer.value == 0:
                # only need to terminate on timeout, otherwise we risk destabilizing
                # the queues
                process.terminate()
                logger.warning(
                    _("reincarnated worker %(name)s after timeout")
                    % {"name": process.name}
                )
            elif int(process.timer.value) == -2:
                logger.info(_("recycled worker %(name)s") % {"name": process.name})
            else:
                logger.error(
                    _("reincarnated worker %(name)s after death")
                    % {"name": process.name}
                )

        self.reincarnations += 1

    def spawn_cluster(self):
        self.pool = []
        Stat(self).save()
        # close connections before spawning new process
        if not Conf.SYNC:
            db.connections.close_all()
        # spawn worker pool
        for __ in range(self.pool_size):
            self.spawn_worker()
        # spawn auxiliary
        self.monitor = self.spawn_monitor()
        self.pusher = self.spawn_pusher()
        # set worker cpu affinity if needed
        if psutil and Conf.CPU_AFFINITY:
            set_cpu_affinity(Conf.CPU_AFFINITY, [w.pid for w in self.pool])

    def guard(self):
        logger.info(
            _("%(name)s guarding cluster %(cluster_name)s")
            % {
                "name": current_process().name,
                "cluster_name": humanize(self.cluster_id.hex),
            }
        )
        self.start_event.set()
        Stat(self).save()
        logger.info(
            _("Q Cluster %(cluster_name)s running.")
            % {"cluster_name": humanize(self.cluster_id.hex)}
        )
        counter = 0
        cycle = Conf.GUARD_CYCLE  # guard loop sleep in seconds
        # Guard loop. Runs at least once
        while not self.stop_event.is_set() or not counter:
            # Check Workers
            for p in self.pool:
                with p.timer.get_lock():
                    # Are you alive?
                    if not p.is_alive() or p.timer.value == 0:
                        self.reincarnate(p)
                        continue
                    # Decrement timer if work is being done
                    if p.timer.value > 0:
                        p.timer.value -= cycle
            # Check Monitor
            if not self.monitor.is_alive():
                self.reincarnate(self.monitor)
            # Check Pusher
            if not self.pusher.is_alive():
                self.reincarnate(self.pusher)
            # Call scheduler once a minute (or so)
            counter += cycle
            if counter >= 30 and Conf.SCHEDULER:
                counter = 0
                scheduler(broker=self.broker)
            # Save current status
            Stat(self).save()
            sleep(cycle)
        self.stop()

    def stop(self):
        Stat(self).save()
        name = current_process().name
        logger.info(_("%(name)s stopping cluster processes") % {"name": name})
        # Stopping pusher
        self.event_out.set()
        # Wait for it to stop
        while self.pusher.is_alive():
            sleep(0.1)
            Stat(self).save()
        # Put poison pills in the queue
        for __ in range(len(self.pool)):
            self.task_queue.put("STOP")
        self.task_queue.close()
        # wait for the task queue to empty
        self.task_queue.join_thread()
        # Wait for all the workers to exit
        while len(self.pool):
            for p in self.pool:
                if not p.is_alive():
                    self.pool.remove(p)
            sleep(0.1)
            Stat(self).save()
        # Finally stop the monitor
        self.result_queue.put("STOP")
        self.result_queue.close()
        # Wait for the result queue to empty
        self.result_queue.join_thread()
        logger.info(_("%(name)s waiting for the monitor.") % {"name": name})
        # Wait for everything to close or time out
        count = 0
        if not self.timeout:
            self.timeout = 30
        while self.status() == Conf.STOPPING and count < self.timeout * 10:
            sleep(0.1)
            Stat(self).save()
            count += 1
        # Final status
        Stat(self).save()


def pusher(task_queue: Queue, event: Event, broker: Broker = None):
    """
    Pulls tasks of the broker and puts them in the task queue
    :type broker:
    :type task_queue: multiprocessing.Queue
    :type event: multiprocessing.Event
    """
    if not broker:
        broker = get_broker()
    logger.info(
        _("%(process_name)s pushing tasks at %(id)s")
        % {"process_name": current_process().name, "id": current_process().pid}
    )
    while True:
        try:
            task_set = broker.dequeue()
        except Exception as e:
            logger.exception("Failed to pull task from broker")
            # broker probably crashed. Let the sentinel handle it.
            sleep(10)
            break
        if task_set:
            for task in task_set:
                ack_id = task[0]
                # unpack the task
                try:
                    task = SignedPackage.loads(task[1])
                except (TypeError, BadSignature) as e:
                    logger.exception("Failed to push task to queue")
                    broker.fail(ack_id)
                    continue
                task["ack_id"] = ack_id
                task_queue.put(task)
            logger.debug(
                _("queueing from %(list_key)s") % {"list_key": broker.list_key}
            )
        if event.is_set():
            break
    logger.info(_("%(name)s stopped pushing tasks") % {"name": current_process().name})


def monitor(result_queue: Queue, broker: Broker = None):
    """
    Gets finished tasks from the result queue and saves them to Django
    :type broker: brokers.Broker
    :type result_queue: multiprocessing.Queue
    """
    if not broker:
        broker = get_broker()
    name = current_process().name
    logger.info(
        _("%(name)s monitoring at %(id)s") % {"name": name, "id": current_process().pid}
    )
    for task in iter(result_queue.get, "STOP"):
        # save the result
        if task.get("cached", False):
            save_cached(task, broker)
        else:
            save_task(task, broker)
        # acknowledge result
        ack_id = task.pop("ack_id", False)
        if ack_id and (task["success"] or task.get("ack_failure", False)):
            broker.acknowledge(ack_id)
        # signal execution done
        post_execute.send(sender="django_q", task=task)
        # log the result
        info_name = get_func_repr(task["func"])
        if task["success"]:
            # log success
            logger.info(
                _("Processed '%(info_name)s' (%(task_name)s)")
                % {"info_name": info_name, "task_name": task["name"]}
            )
        else:
            # log failure
            logger.error(
                _("Failed '%(info_name)s' (%(task_name)s) - %(task_result)s")
                % {
                    "info_name": info_name,
                    "task_name": task["name"],
                    "task_result": task["result"],
                }
            )
    logger.info(_("%(name)s stopped monitoring results") % {"name": name})


def worker(
    task_queue: Queue, result_queue: Queue, timer: Value, timeout: int = Conf.TIMEOUT
):
    """
    Takes a task from the task queue, tries to execute it and puts the result back in
    the result queue
    :param timeout: number of seconds wait for a worker to finish.
    :type task_queue: multiprocessing.Queue
    :type result_queue: multiprocessing.Queue
    :type timer: multiprocessing.Value
    """
    proc_name = current_process().name
    logger.info(
        _("%(proc_name)s ready for work at %(id)s")
        % {"proc_name": proc_name, "id": current_process().pid}
    )
    task_count = 0
    if timeout is None:
        timeout = -1
    # Start reading the task queue
    for task in iter(task_queue.get, "STOP"):
        result = None
        timer.value = -1  # Idle
        task_count += 1
        # Get the function from the task
        func = task["func"]
        func_name = get_func_repr(func)
        logger.info(
            _("%(proc_name)s processing '%(func_name)s' (%(task_name)s)")
            % {
                "proc_name": proc_name,
                "func_name": func_name,
                "task_name": task["name"],
            }
        )
        f = task["func"]
        # if it's not an instance try to get it from the string
        if not callable(task["func"]):
            f = pydoc.locate(f)
        close_old_django_connections()
        timer_value = task.pop("timeout", timeout)
        # signal execution
        pre_execute.send(sender="django_q", func=f, task=task)
        # execute the payload
        timer.value = timer_value  # Busy
        try:
            res = f(*task["args"], **task["kwargs"])
            result = (res, True)
        except Exception as e:
            result = (f"{e} : {traceback.format_exc()}", False)
            if error_reporter:
                error_reporter.report()
            if task.get("sync", False):
                raise
        with timer.get_lock():
            # Process result
            task["result"] = result[0]
            task["success"] = result[1]
            task["stopped"] = timezone.now()
            result_queue.put(task)
            timer.value = -1  # Idle
            # Recycle
            if task_count == Conf.RECYCLE or rss_check():
                timer.value = -2  # Recycled
                break
    logger.info(_("%(proc_name)s stopped doing work") % {"proc_name": proc_name})


def save_task(task, broker: Broker):
    """
    Saves the task package to Django or the cache
    :param task: the task package
    :type broker: brokers.Broker
    """
    # SAVE LIMIT < 0 : Don't save success
    if not task.get("save", Conf.SAVE_LIMIT >= 0) and task["success"]:
        return
    # enqueues next in a chain
    if task.get("chain", None):
        django_q.tasks.async_chain(
            task["chain"],
            group=task["group"],
            cached=task["cached"],
            sync=task["sync"],
            broker=broker,
        )
    # SAVE LIMIT > 0: Prune database, SAVE_LIMIT 0: No pruning
    close_old_django_connections()

    try:
        filters = {}
        if (
            Conf.SAVE_LIMIT_PER
            and Conf.SAVE_LIMIT_PER in {"group", "name", "func"}
            and Conf.SAVE_LIMIT_PER in task
        ):
            value = task[Conf.SAVE_LIMIT_PER]
            if Conf.SAVE_LIMIT_PER == "func":
                value = get_func_repr(value)
            filters[Conf.SAVE_LIMIT_PER] = value

        database_to_use = (
            {"using": Conf.ORM if Conf.ORM else Schedule.objects.db}
            if not Conf.HAS_REPLICA
            else {}
        )
        with db.transaction.atomic(**database_to_use):
            last = Success.objects.filter(**filters).select_for_update().last()
            if (
                task["success"]
                and 0 < Conf.SAVE_LIMIT <= Success.objects.filter(**filters).count()
            ):
                last.delete()

        # check if this task has previous results
        try:
            existing_task = Task.objects.get(id=task["id"], name=task["name"])
            # only update the result if it hasn't succeeded yet
            if not existing_task.success:
                existing_task.stopped = task["stopped"]
                existing_task.result = task["result"]
                existing_task.success = task["success"]
                existing_task.attempt_count = existing_task.attempt_count + 1
                existing_task.save()

            if (
                Conf.MAX_ATTEMPTS > 0
                and existing_task.attempt_count >= Conf.MAX_ATTEMPTS
            ):
                broker.acknowledge(task["ack_id"])

        except Task.DoesNotExist:
            # convert func to string
            func = get_func_repr(task["func"])
            Task.objects.create(
                id=task["id"],
                name=task["name"],
                func=func,
                hook=task.get("hook"),
                args=task["args"],
                kwargs=task["kwargs"],
                started=task["started"],
                stopped=task["stopped"],
                result=task["result"],
                group=task.get("group"),
                success=task["success"],
                attempt_count=1,
            )
    except Exception as e:
        logger.error(e)


def save_cached(task, broker: Broker):
    task_key = f'{broker.list_key}:{task["id"]}'
    timeout = task["cached"]
    if timeout is True:
        timeout = None
    try:
        group = task.get("group", None)
        iter_count = task.get("iter_count", 0)
        # if it's a group append to the group list
        if group:
            group_key = f"{broker.list_key}:{group}:keys"
            group_list = broker.cache.get(group_key) or []
            # if it's an iter group, check if we are ready
            if iter_count and len(group_list) == iter_count - 1:
                group_args = f"{broker.list_key}:{group}:args"
                # collate the results into a Task result
                results = [
                    SignedPackage.loads(broker.cache.get(k))["result"]
                    for k in group_list
                ]
                results.append(task["result"])
                task["result"] = results
                task["id"] = group
                task["args"] = SignedPackage.loads(broker.cache.get(group_args))
                task.pop("iter_count", None)
                task.pop("group", None)
                if task.get("iter_cached", None):
                    task["cached"] = task.pop("iter_cached", None)
                    save_cached(task, broker=broker)
                else:
                    save_task(task, broker)
                broker.cache.delete_many(group_list)
                broker.cache.delete_many([group_key, group_args])
                return
            # save the group list
            group_list.append(task_key)
            broker.cache.set(group_key, group_list, timeout)
            # async_task next in a chain
            if task.get("chain", None):
                django_q.tasks.async_chain(
                    task["chain"],
                    group=group,
                    cached=task["cached"],
                    sync=task["sync"],
                    broker=broker,
                )
        # save the task
        broker.cache.set(task_key, SignedPackage.dumps(task), timeout)
    except Exception as e:
        logger.error(e)


def scheduler(broker: Broker = None):
    """
    Creates a task from a schedule at the scheduled time and schedules next run
    """
    if not broker:
        broker = get_broker()
    close_old_django_connections()
    try:
        database_to_use = (
            {"using": Conf.ORM if Conf.ORM else Schedule.objects.db}
            if not Conf.HAS_REPLICA
            else {}
        )
        with db.transaction.atomic(**database_to_use):
            for s in (
                Schedule.objects.select_for_update()
                .exclude(repeats=0)
                .filter(next_run__lt=timezone.now())
                .filter(
                    db.models.Q(cluster__isnull=True) | db.models.Q(cluster=Conf.PREFIX)
                )
            ):
                args = ()
                kwargs = {}
                # get args, kwargs and hook
                if s.kwargs:
                    try:
                        # first try the dict syntax
                        kwargs = ast.literal_eval(s.kwargs)
                    except (SyntaxError, ValueError):
                        # else use the kwargs syntax
                        try:
                            parsed_kwargs = (
                                ast.parse(f"f({s.kwargs})").body[0].value.keywords
                            )
                            kwargs = {
                                kwarg.arg: ast.literal_eval(kwarg.value)
                                for kwarg in parsed_kwargs
                            }
                        except (SyntaxError, ValueError):
                            kwargs = {}
                if s.args:
                    args = ast.literal_eval(s.args)
                    # single value won't eval to tuple, so:
                    if type(args) != tuple:
                        args = (args,)
                q_options = kwargs.get("q_options", {})
                if s.hook:
                    q_options["hook"] = s.hook
                # set up the next run time
                if s.schedule_type != s.ONCE:
                    next_run = s.next_run
                    while True:
                        next_run = s.calculate_next_run(next_run)
                        if Conf.CATCH_UP or next_run > localtime():
                            break

                    s.next_run = next_run
                    s.repeats += -1
                # send it to the cluster
                scheduled_broker = broker
                try:
                    scheduled_broker = get_broker(q_options["broker_name"])
                except:  # noqa: E722
                    # invalid broker_name or non existing broker with broker_name
                    pass
                q_options["broker"] = scheduled_broker
                q_options["group"] = q_options.get("group", s.name or s.id)
                kwargs["q_options"] = q_options
                s.task = django_q.tasks.async_task(s.func, *args, **kwargs)
                # log it
                if not s.task:
                    logger.error(
                        _(
                            "%(process_name)s failed to create a task from schedule "
                            "[%(schedule)s]"
                        )
                        % {
                            "process_name": current_process().name,
                            "schedule": s.name or s.id,
                        }
                    )
                else:
                    logger.info(
                        _(
                            "%(process_name)s created a task from schedule "
                            "[%(schedule)s]"
                        )
                        % {
                            "process_name": current_process().name,
                            "schedule": s.name or s.id,
                        }
                    )
                # default behavior is to delete a ONCE schedule
                if s.schedule_type == s.ONCE:
                    if s.repeats < 0:
                        s.delete()
                        continue
                    # but not if it has a positive repeats
                    s.repeats = 0
                # save the schedule
                s.save()
    except Exception as e:
        logger.error(e)


def close_old_django_connections():
    """
    Close django connections unless running with sync=True.
    """
    if Conf.SYNC:
        logger.warning(
            "Preserving django database connections because sync=True. Beware "
            "that tasks are now injected in the calling context/transactions "
            "which may result in unexpected behaviour."
        )
    else:
        db.close_old_connections()


def set_cpu_affinity(n: int, process_ids: list, actual: bool = not Conf.TESTING):
    """
    Sets the cpu affinity for the supplied processes.
    Requires the optional psutil module.
    :param int n: affinity
    :param list process_ids: a list of pids
    :param bool actual: Test workaround for Travis not supporting cpu affinity
    """
    # check if we have the psutil module
    if not psutil:
        logger.warning(_("Skipping cpu affinity because psutil was not found."))
        return
    # check if the platform supports cpu_affinity
    if actual and not hasattr(psutil.Process(process_ids[0]), "cpu_affinity"):
        logger.warning(
            _("Faking cpu affinity because it is not supported on this platform")
        )
        actual = False
    # get the available processors
    cpu_list = list(range(psutil.cpu_count()))
    # affinities of 0 or gte cpu_count, equals to no affinity
    if not n or n >= len(cpu_list):
        return
    # spread the workers over the available processors.
    index = 0
    for pid in process_ids:
        affinity = []
        for k in range(n):
            if index == len(cpu_list):
                index = 0
            affinity.append(cpu_list[index])
            index += 1
        if psutil.pid_exists(pid):
            p = psutil.Process(pid)
            if actual:
                p.cpu_affinity(affinity)
            logger.info(
                _("%(pid)s will use cpu %(affinity)s")
                % {"pid": pid, "affinity": affinity}
            )


def rss_check():
    if Conf.MAX_RSS:
        if resource:
            return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss >= Conf.MAX_RSS
        elif psutil:
            return psutil.Process().memory_info().rss >= Conf.MAX_RSS * 1024
    return False
