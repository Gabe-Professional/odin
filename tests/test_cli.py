import os
import subprocess
import shutil
import pytest
from tests.fixture import start_time, end_time, tmp_dir


def test_cli(start_time, end_time, tmp_dir):
    # todo: this seems to work but does not return anything with the current parameters...needs fixing...
    subdirs = ['test_1', 'test_2']
    cmd = 'odin collect '
    cmd += f'--project_directory {tmp_dir} --sub_directories {subdirs[0]} {subdirs[1]} --database postgres ' \
           f'--start_time {start_time} --end_time {end_time} --message_direction in'

    subprocess.check_output(cmd, shell=True)
    # todo: this part of the test works...so it is taking the parameters...just not showing the returned query...
    #  add a save input to test more...
    assert os.path.exists(tmp_dir)
    shutil.rmtree(tmp_dir)
