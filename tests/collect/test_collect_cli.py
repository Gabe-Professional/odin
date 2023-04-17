import subprocess
import os
import shutil
from tests.fixture import start_time, end_time, tmp_dir


def test_collect_cli(start_time, end_time, tmp_dir):
    subdirs = ['test_1', 'test_2']
    direction = 'in'
    cmd = 'odin collect '
    cmd += f'-d {tmp_dir} -sd {subdirs[0]} {subdirs[1]} -db postgres ' \
           f'-st {start_time} -et {end_time} -md {direction} -v'

    output = subprocess.check_output(cmd, shell=True)
    for o in str(output, 'UTF-8').split('\n'):
        print(o)

    assert os.path.exists(tmp_dir)
    shutil.rmtree(tmp_dir)