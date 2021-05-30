import random

# External
import redis

# Django
from django.utils.translation import gettext_lazy as _
from redis import Redis

from django_q.brokers import Broker
from django_q.conf import Conf


class Disque(Broker):
    def enqueue(self, task):
        retry = Conf.RETRY if Conf.RETRY > 0 else f"{Conf.RETRY} REPLICATE 1"
        return self.connection.execute_command(
            f"ADDJOB {self.list_key} {task} 500 RETRY {retry}"
        ).decode()

    def dequeue(self):
        tasks = self.connection.execute_command(
            f"GETJOB COUNT {Conf.BULK} TIMEOUT 1000 FROM {self.list_key}"
        )
        if tasks:
            return [(t[1].decode(), t[2].decode()) for t in tasks]

    def queue_size(self):
        return self.connection.execute_command(f"QLEN {self.list_key}")

    def acknowledge(self, task_id):
        command = "FASTACK" if Conf.DISQUE_FASTACK else "ACKJOB"
        return self.connection.execute_command(f"{command} {task_id}")

    def ping(self) -> bool:
        return self.connection.execute_command("HELLO")[0] > 0

    def delete(self, task_id):
        return self.connection.execute_command(f"DELJOB {task_id}")

    def fail(self, task_id):
        return self.delete(task_id)

    def delete_queue(self) -> int:
        jobs = self.connection.execute_command(f"JSCAN QUEUE {self.list_key}")[1]
        if jobs:
            job_ids = " ".join(jid.decode() for jid in jobs)
            self.connection.execute_command(f"DELJOB {job_ids}")
        return len(jobs)

    def info(self) -> str:
        if not self._info:
            info = self.connection.info("server")
            self._info = f'Disque {info["disque_version"]}'
        return self._info

    @staticmethod
    def get_connection(list_key: str = Conf.PREFIX) -> Redis:
        if not Conf.DISQUE_NODES:
            raise redis.exceptions.ConnectionError(_("No Disque nodes configured"))
        # randomize nodes
        random.shuffle(Conf.DISQUE_NODES)
        # find one that works
        for node in Conf.DISQUE_NODES:
            host, port = node.split(":")
            kwargs = {"host": host, "port": port}
            if Conf.DISQUE_AUTH:
                kwargs["password"] = Conf.DISQUE_AUTH
            redis_client = redis.Redis(**kwargs)
            redis_client.decode_responses = True
            try:
                redis_client.execute_command("HELLO")
                return redis_client
            except redis.exceptions.ConnectionError:
                continue
        raise redis.exceptions.ConnectionError(
            _("Could not connect to any Disque nodes")
        )
