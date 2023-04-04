import os
import subprocess
import shutil
import pytest
from tests.fixture import start_time, end_time, tmp_dir


def test_cli(start_time, end_time, tmp_dir):
    subdirs = ['test_1', 'test_2']
    direction = 'in'
    cmd = 'odin collect '
    cmd += f'--project_directory {tmp_dir} --sub_directories {subdirs[0]} {subdirs[1]} --database postgres ' \
           f'--start_time {start_time} --end_time {end_time} --message_direction {direction} -v'

    subprocess.check_output(cmd, shell=True)
    assert os.path.exists(tmp_dir)
    shutil.rmtree(tmp_dir)
    # todo: test the failure of the functions as well...
