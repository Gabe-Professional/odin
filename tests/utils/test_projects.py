import os

import odin.utils.projects as projects
import shutil
import logging
logger = logging.getLogger('odin')


def test_logging():
    logger.info("this is logging info")
    print(logger.info('test'))


def test_setup_project_directory(tmpdir):
    subdirs = ['test_a', 'test_b', 'test_c']
    dirs = projects.setup_project_directory(tmpdir, subdirs=subdirs)
    print(dirs)
    assert set(os.listdir(tmpdir)) == set(dirs.keys())
    for d in dirs.values():
        assert os.path.exists(d)
    # REMOVE THE TEST DIRECTORY
    shutil.rmtree(tmpdir)

    # TEST DEFAULT DIRECTORIES
    dirs = projects.setup_project_directory(tmpdir)
    assert set(os.listdir(tmpdir)) == {'data', 'plots'}
    for d in dirs.values():
        assert os.path.exists(d)
    shutil.rmtree(tmpdir)




