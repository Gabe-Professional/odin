#!/bin/bash
set -xe

docker run -it --rm -v ${HOME}/.odin:/home/user/.odin odin-analytics $*