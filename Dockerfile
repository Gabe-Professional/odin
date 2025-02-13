# ##########################  Main ODIN Docker Image ############################
# This Dockerfile is used for building and testing the ODIN library
#
# To build the ODIN image you can use the helper script
#       -> ./docker-build.sh
#
# To use this Dockerfile to test the ODIN build you can use the helper script
#       -> ./docker-test.sh [WIP]
#
#
# ################################################################################


FROM ubuntu:22.04 as build
RUN apt update
RUN apt install -y git
RUN apt-get update
RUN echo 'Installing python3...'
RUN apt -y install python3 python3-pip bash python3.10-venv
RUN useradd -ms /bin/bash user
RUN echo 'Adding the odin repository'
ADD . /home/user/build/odin
RUN chown -R user /home/user/
USER user
RUN echo 'Setting the working directory to odin'
WORKDIR /home/user/build/odin
RUN python3 -m venv venv
RUN echo 'Making the directories for scripts'
RUN mkdir /home/user/projects
RUN mkdir /home/user/projects/odin
RUN mkdir /home/user/projects/odin/rfj_alerting_app
RUN mkdir /home/user/projects/odin/rfj_alerting_app/data
RUN mkdir /home/user/projects/odin/rfj_alerting_app/data/model
ENV PATH="/home/user/build/odin/venv/bin:$PATH"
RUN echo 'Installing the odin requirements file'
RUN pip3 install -r requirements.txt
RUN pip3 install -e .
VOLUME /home/user/projects
# build the testing stage
FROM ubuntu:22.04 AS test
RUN apt update
RUN apt install -y git
RUN apt-get update
RUN echo 'Installing python3...'
RUN apt -y install python3 python3-pip bash python3.10-venv
RUN useradd -ms /bin/bash user
ADD . /home/user/test/odin
WORKDIR /home/user/test/odin
RUN python3 -m venv venv
ENV PATH="/home/user/test/odin/venv/bin:$PATH"
RUN pip3 install -r requirements.txt
RUN pip3 install -e .
CMD ["pytest", "/home/user/test/odin/tests", "-v"]
