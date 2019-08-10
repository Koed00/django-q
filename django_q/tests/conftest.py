import contextlib
import os
import re
import subprocess

import pytest


@pytest.fixture
def ironmq_config():
    token = os.getenv('IRON_MQ_TOKEN')
    project_id = os.getenv('IRON_MQ_PROJECT_ID')
    if token and project_id:
        yield {'token': token,
               'project_id': project_id}

    elif _is_ironmq_running_locally():
        with _temp_ironmq_project() as (user_token, project_id):
            yield {'token': user_token,
                   'project_id': project_id,
                   'host': 'localhost',
                   'port': 8080,
                   'protocol': 'http'}

    else:
        pytest.skip("Requires IronMQ credentials or running IronMQ locally")


def _is_ironmq_running_locally():
    try:
        p = subprocess.run(
            # This assumes that IronMQ is running in a Docker container started with command
            # docker-compose --project-name django-q -f test-services-docker-compose.yaml up
            ('docker', 'ps', '-q', '-f', 'name=django-q_ironmq_1'),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        return bool(p.stdout.strip())

    except FileNotFoundError:
        # docker command not available
        return False


@contextlib.contextmanager
def _temp_ironmq_project():
    # Just make sure the user does not exist due to earlier run
    _run_auth_cli('delete', 'user', 'ironmq@example.org')

    p = _run_auth_cli(
        'create',
        'user',
        'ironmq@example.org',
        'password',
    )
    assert p.returncode == 0, 'Failed to create user in IronMQ: {}'.format(p.stdout)

    m = re.match(
        r'.*msg="user created successfully".*id=(?P<id>[0-9a-f]+)\s.*token=(?P<token>[^\s]+).*',
        p.stdout.strip(),
    )
    assert m, 'Unexpected user created message: {}'.format(p.stdout)

    user_id = m.group('id')
    user_token = m.group('token')
    if not user_id or not user_token:
        pytest.skip('No IronMQ credentials provided and IronMQ not running locally.')

    p = _run_auth_cli(
        '-t', user_token,
        'create',
        'project',
        'django-q-test',
    )
    assert p.returncode == 0, 'Failed to create IronMQ project: {}'.format(p.stdout)

    m = re.match(
        r'.*msg="project created successfully".*id=(?P<id>[0-9a-f]+)\s.*',
        p.stdout.strip(),
    )
    assert m, 'Unexpected project created message: {}'.format(p.stdout)

    project_id = m.group('id')

    yield user_token, project_id

    p = _run_auth_cli('delete', 'user', user_id)
    assert p.returncode == 0, 'Failed to remove user from IronMQ: {}'.format(p.stdout)


def _run_auth_cli(*args):
    return subprocess.run(
        (
            'docker',
            'run',
            '--network', 'django-q_test',
            'iron/authcli',
            'iron',
            '-h', 'http://ironauth:8090',
            '-t', 'adminToken',
            *args,
        ),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )
