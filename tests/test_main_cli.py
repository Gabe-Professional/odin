import os
import subprocess
import shutil
import pytest
from tests.fixture import start_time, end_time, tmp_dir
import logging
logger = logging.getLogger(__name__)


def test_cli_args(start_time, end_time, tmp_dir):
    # todo: need to query less data
    cmd = 'odin collect '
    cmd += f'-d {tmp_dir} -sd test1 test2 -st {start_time} -et {end_time} -db elastic -c PROD -kw biden nato -v'
    output = subprocess.check_output(cmd, shell=True)
    for o in str(output, 'UTF-8').split('\n'):
        print(o)

    assert os.path.exists(tmp_dir)

    shutil.rmtree(tmp_dir)
