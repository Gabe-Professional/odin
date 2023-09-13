import os
import logging
logger = logging.getLogger(__name__)


def setup_project_directory(directory, subdirs=None):

    directory = os.path.expanduser(directory)

    if not os.path.exists(directory):
        logger.info(f"Creating New Project Directory: {directory}")
        os.makedirs(directory)
        if subdirs is not None:
            dirs = {name: os.path.join(directory, name) for name in subdirs}

            # CREATE THE SUBDIRECTORIES
            for n, d in dirs.items():
                if not os.path.exists(d):
                    logger.info(f'Creating Project {n} Directory: {d}')
                    os.makedirs(d)
                else:
                    logger.info(f'Directory {d} already exists...continuing')
        else:
            subdirs = ['data', 'plots']
            dirs = {name: os.path.join(directory, name) for name in subdirs}
            logger.info(f'Setting subdirectories to default {subdirs}')
            # CREATE THE SUBDIRECTORIES
            for n, d in dirs.items():
                if not os.path.exists(d):
                    logger.info(f'Creating Project {n} Directory: {d}')
                    os.makedirs(d)
                else:
                    logger.info(f'Directory {d} already exists...continuing')

    else:
        subdirs = ['data', 'plots']
        dirs = {name: os.path.join(directory, name) for name in subdirs}
        for n, d in dirs.items():
            if not os.path.exists(d):
                logger.info(f'Creating Project {n} Directory: {d}')
                os.makedirs(d)
            else:
                logger.info(f'Directory {d} already exists...continuing')

    return dirs


def project_main(args):
    directory = args.project_directory
    subdirs = args.sub_dirs
    dirs = setup_project_directory(directory=directory, subdirs=subdirs)
    # todo: make a meta file for project main arg parse to track datetimes
