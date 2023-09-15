import os
import subprocess
import shutil
# from tests.fixture import start_time, end_time
import logging
logger = logging.getLogger(__name__)


def test_cli_args(start_time, end_time, tmpdir):
    # todo: need to query less data

    cmd = 'odin collect '
    cmd += f'--elastic -d {tmpdir} -sd test1 test2 -a {start_time} -b {end_time} -c PROD -kw biden nato -v'
    output = subprocess.check_output(cmd, shell=True)
    for o in str(output, 'UTF-8').split('\n'):
        print(o)

    assert os.path.exists(tmpdir)

    shutil.rmtree(tmpdir)
