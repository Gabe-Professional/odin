#!/bin/bash
set -xe

docker run -it --rm -v ${HOME}/.odin:/home/user/.odin \
                    -v ${HOME}/projects/odin/rfj_alerting_app/data/model:/home/user/projects/odin/rfj_alerting_app/data/model registry.appbucket.io/odin/odin-analytics $*

