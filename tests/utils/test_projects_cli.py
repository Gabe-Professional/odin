import shutil
import subprocess
import os


def test_project_cli(tmpdir):
    subdirs = ['test_1', 'test_2']
    cmd = 'odin project '
    cmd += f'--project_directory {tmpdir} --sub_dirs {subdirs[0]} {subdirs[1]} -v'

    output = subprocess.check_output(cmd, shell=True)
    for o in str(output, 'UTF-8').split("\n"):
        print(o)
    assert os.path.exists(tmpdir)
    shutil.rmtree(tmpdir)
