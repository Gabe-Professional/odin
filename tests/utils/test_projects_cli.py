import shutil
import subprocess
import os
from tests.fixture import tmp_dir


def test_project_cli(tmp_dir):
    subdirs = ['test_1', 'test_2']
    cmd = 'odin project '
    cmd += f'--project_directory {tmp_dir} --sub_dirs {subdirs[0]} {subdirs[1]} -v'

    output = subprocess.check_output(cmd, shell=True)
    for o in str(output, 'UTF-8').split("\n"):
        print(o)
    assert os.path.exists(tmp_dir)
    shutil.rmtree(tmp_dir)
