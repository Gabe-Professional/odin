import os

import odin.utils.projects as projects
import shutil
import logging
from tests.fixture import tmp_dir
logger = logging.getLogger('odin')


def test_logging():
    logger.info("this is logging info")
    print(logger.info('test'))


def test_setup_project_directory(tmp_dir):
    subdirs = ['test_a', 'test_b', 'test_c']
    dirs = projects.setup_project_directory(tmp_dir, subdirs=subdirs)
    print(dirs)
    assert set(os.listdir(tmp_dir)) == set(dirs.keys())
    for d in dirs.values():
        assert os.path.exists(d)
    # REMOVE THE TEST DIRECTORY
    shutil.rmtree(tmp_dir)

    # TEST DEFAULT DIRECTORIES
    dirs = projects.setup_project_directory(tmp_dir)
    assert set(os.listdir(tmp_dir)) == {'data', 'plots'}
    for d in dirs.values():
        assert os.path.exists(d)
    shutil.rmtree(tmp_dir)




