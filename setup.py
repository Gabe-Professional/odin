from setuptools import setup, find_packages
#
# with open("README.md", "r", encoding="utf-8") as fh:
#     long_description = fh.read()
#
#
# setup(
#     name="odin",  # Replace with your package name
#     use_scm_version=True,  # Use setuptools_scm to determine version
#     author="Gabe McBride",
#     author_email="gabriel.mcbride@twosixtech.com",
#     description="Odin analytics cli tools",
#     long_description="Read the README.md for more details.",  # You can load from file if needed
#     long_description_content_type=long_description,
#     # url="https://github.com/yourusername/my-package",  # Replace with your package's repository URL
#     packages=find_packages(),
#     install_requires=[],  # Add any dependencies your package needs
#     classifiers=[
#         'Private :: Do Not Upload to pypi server outside TwoSixTech'
#     ],
#     setup_requires=["setuptools_scm"],  # Add setuptools_scm as a setup requirement
#     entry_points={
#         "console_scripts": [
#             "odin = odin.cli:run",
#         ],
#     },
# )

from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='odin',
    use_scm_version=True,  # Use setuptools_scm to determine version
    author="Gabe McBride",
    author_email="gabriel.mcbride@twosixtech.com",
    description="Odin Analytics CLI Tools",
    long_description="Read the README.md for more details.",  # You can load from file if needed
    long_description_content_type=long_description,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'odin = odin.cli:run'
        ]
    },
    classifiers=[
        'Private :: Do Not Upload to pypi server outside TwoSixTech'
    ],
)
