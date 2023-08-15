ODIN -- Module to support analytics
===================================================

# Overview
This is a library of analytics tools used extensively by Odin analysts. This package serves as a library of python tooling used for querying, summarizing, and visualizing `odin` data from both ElasticSearch and Postgres databases. Additionally, python scripting, which is available in this library, makes use of the `odin` package that supports regular tasking regarding Odin data.  

In addition to providing the capability of assessing Odin data, `odin` provides a set of Command Line Interface (CLI) applications that allow for performing these operations such as, querying data, visualizing data, and running scripts, which provides the capability of customizing analytics projects.

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


# Installation
ODIN requires the following pieces to be in place before you can install the package and use it: 
* python 3 or greater and pip installed on your machine
* you have a .cred folder setup in your home directory with the proper items in it. 

For help with setting up these requirements, contact Gabe McBride

## Installing Python and PIP
Installing Python and PIP on your machine will depend on what operating system you are utilizing. 

If you are using MacOS, starting at the following link will be helpful:

[Installing Python 3 on Mac OS](https://docs.python-guide.org/starting/install3/osx/)

Becoming familiar with some other python packages will also be helpful for making sense of the ODIN data. 
* numpy, scipy, matplotlib
* pandas


## Getting VPN access
VPN access is required to utilize certain parts of `odin`. Please setup your VPN in accordance with the team SOP. 


## General User Installation

Once you have completed the steps above, you are ready to install `odin`. To get started, you will need to clone this repository on your machine and then install the package. After cloning the repo from istresearch/odin github, change your directory to `odin` using:

```bash
cd odin
```

then run:

```bash
$ pip install -e .
```

This will install the application on your machine and you will be able to run the `odin` commands and subcommands.

Users are unable to install `odin` on their machine without cloning the repository at this time. 

# Usage
The main entry point for this application, once ODIN has been installed is `odin` from the commandline. For more details on the specific applications and/or how to run a particular subcommand type: 

```bash
$ odin -h
```

Similarly, for more specific details on particular subcommands, use:

```bash
$ odin <subcommand> -h
```

# Contributing to ODIN

## Developer Installation
Developers can follow the same steps as general users for cloning the repository as general users at this time. 

## Development
Development of `odin` follows the traditional git development cycle and uses different branches to track different development progress. The naming convention for branches should be:

* BUG - "bug/items_do_not_work"
* FEATURE - "feature/adding_new_capability"
* IMPROVEMENT - "improvement/updating_document"


When working, make sure that you:
* branch from master, 
   * use the appropriate naming convention, 
   * make a basic commit and then go ahead and fill out Merge Request as Work In Progress (WIP)
      * Add Details into the merge request about what exactly is happening in this branch so that
        others can track progress and/or contribute when necessary
* write your code and unit tests simultaneously
* merge master into your branch often to minimize conflicts
* commit often
* push somewhat regularly

When you feel your branch is complete, and has passed all tests, change the Merge Request Title, by 
removing the WIP annotation, and assign the Merge Request to a project maintainer:
* Gabe McBride <gabriel.mcbride@twosixtech.com>