ODIN -- Module to support analytics
===================================================

# Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
   1. [Installing Python & PIP](#installing-python-&-pip)
   2. [Getting VPN Access](#getting-vpn-access)
   3. [Setting up](#setting-up)
   4. [General User Installation](#general-user-installation)
3. [Usage](#usage)
4. [Contributing to ODIN](#contributing-to-odin)
   1. [Developer Installation](#developer-installation)

# Overview
This is a library of analytics tools used extensively by Odin analysts. This package serves as a library of python tooling used for querying, summarizing, and visualizing `odin` data from both ElasticSearch and Postgres databases. Additionally, python scripting, which is available in this library, makes use of the `odin` package that supports regular tasking regarding Odin data.  

In addition to providing the capability of assessing Odin data, `odin` provides a set of Command Line Interface (CLI) applications that allow for performing these operations such as, querying data, visualizing data, and running scripts, which provides the capability of customizing analytics projects.


# Installation
ODIN requires the following pieces to be in place before you can install the package and use it: 
* python 3 or greater and pip installed on your machine
* you have a .odin folder setup in your home directory with the proper items in it. 

For help with setting up these requirements, contact Gabe McBride.

## Installing Python and PIP
Installing Python and PIP on your machine will depend on what operating system you are utilizing. 

If you are using MacOS, starting at the following link will be helpful:

[Installing Python 3 on Mac OS](https://docs.python-guide.org/starting/install3/osx/)

Becoming familiar with some other python packages will also be helpful for making sense of the ODIN data. 
* numpy, scipy, matplotlib
* pandas


## Getting VPN access
VPN access is required to utilize certain parts of `odin`. Please set up your VPN in accordance with the team's (standard operating procedures) SOP. 


## General User Installation

There are a few ways you can utilize the odin analytics tools, which will depend on your level of comfort. For general users (i.e. analysts), the easiest way to utilize these tools will be to make use of docker desktop. Please contact Engineering and Data for help with this if you are unable to do so. Once docker is installed, you will be able to pull the image onto your local machine with:

```bash
$ docker login <registry>
```

when prompted, enter the username and password for the registry. If you haven't been given these items, please contact Engineering and Data. 

Once logged in, run:

```bash
$ docker pull <image>
```
Once the pull is complete, you will be able to run the image interactively to make use of the odin analytics tools!

## Developer Installation
If you would like to contribute to the development of the odin analytics tools, you will need to complete the initial [Installation](#installation) instructions from above, and you can skip the general user instructions (unless you would like to make use of docker as well). Once the initial installation items are completed, you'll need to clone the repository onto your machine. After that, navigate into the odin directory with:

```bash
$ ~/some-folder/odin
```

from there, run:

```bash
$ pip install -e .
```
to install the commandline tool locally on your machine. 

# Usage
The main entry point for this application, once ODIN has been installed, is `odin` from the commandline. For more details on the specific applications and/or how to run a particular subcommand type: 

```bash
$ odin -h
```

Similarly, for more specific details on particular subcommands, use:

```bash
$ odin <subcommand> -h
```

# Contributing to ODIN

## Development
Development of `odin` follows the traditional git development cycle and uses different branches to track different development progress. The naming convention for branches should represent the work that is tracked in JIRA using issue types. For example:

* EPIC - `epic/OD-000_new-feature`
* STORY - `story/OD-000_add-improvement`
* BUG - `bug/OD-000_broken-item`
* TASK - `task/OD-000_add-item`

The format for new branches is generally,

`issue_type/issue-key_issue-summary`, where the issue-summary of your JIRA ticket is 'function noun'. Just do your best to make the issue summary short and straightforward! 

Workload is also generally inherent to the issue type. For example, EPICs are usually a larger effort compared to STORY and TASK. STORY, BUG, and TASK can also exist in JIRA as independent work or can be thought of as sub-categories of EPICs. There may be some overlap between issue types at times, just do your best to containerize your work!

When working, make sure that you:
* branch from master, 
   * use the appropriate naming convention, 
   * make a basic commit and then go ahead and fill out Pull Request (PR) as Work In Progress (WIP) by appending [WIP] to the front of your PR title. This is usually your branch name initially (i.e. `[WIP]/branch-name`). 
      * Add Details into the pull request about what exactly is happening in this branch so that others can track progress and/or contribute when necessary
* write your code and unit tests simultaneously
* merge master into your branch while you are developing often to minimize conflicts
* commit often
* push to your remote branch somewhat regularly
* do not push to master (unless it is coordinated with a maintainer.) 

When you feel your branch is complete, and has passed all tests locally, change the PR title, by 
removing the WIP annotation, and assign the Merge Request to a project maintainer for review:
* Gabe McBride <gabriel.mcbride@twosixtech.com>

## Testing

Testing the `odin` analytics package is somewhat built into the development process by utilizing github actions. The repository uses two workflow files, `docker-image.yml` and `docker-test.yml`. On pushes to non-master branches and PRs, github actions will run the `docker-test.yml` file, which will build the `odin` image and run the unit tests using `pytest`. The workflow will output any failed tests and result in a failed build. From there, the developer can troubleshoot any issues with failed tests. It is also recommended that you run the unit tests locally on your machine to sort out any failures prior to pushing your work. You can use the helper files `docker-build.sh` and `docker-test.sh` to do this. Once a PR is merged into master, github actions will run the `docker-image.yml` workflow, which will first execute the unit tests. Given the tests pass, the workflow will then deploy the image to the Odin registry where it can then be utilized by other users. 

### Writing Tests
Unit tests for `odin` live in the `/tests/` directory. From there, every sub-directory of `odin` has its own testing directory. For example, tests for `/odin/collect/some_file.py` live in `tests/collect/test_some_file.py`. Generally, each `.py` file in `odin` also has its own test file where there is a unit test for each function in that file. 