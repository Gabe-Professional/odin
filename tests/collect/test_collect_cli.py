import subprocess
import os
import shutil


def test_collect_cli(start_time, end_time, tmpdir):
    subdirs = ['test_1', 'test_2']
    cmd = 'odin collect '
    cmd += f'--postgres -d {tmpdir} -sd {subdirs[0]} {subdirs[1]} ' \
           f'-a {start_time} -b {end_time} -i -v'

    output = subprocess.check_output(cmd, shell=True)
    for o in str(output, 'UTF-8').split('\n'):
        print(o)

    assert os.path.exists(tmpdir)
    shutil.rmtree(tmpdir)