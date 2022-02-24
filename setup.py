from setuptools import setup

install_deps = []

setup(
    name='odin',
    version='0.0.1',
    packages=['odin'],
    # install_requires=install_deps,
    entry_points={
        'console_scripts': [
            'odin = odin.cli:run'
        ]
    }
)
