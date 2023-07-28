FROM ubuntu:22.04
RUN apt update
RUN apt -y install python3 python3-pip bash python3.10-venv
RUN useradd -ms /bin/bash user
ADD . /home/user/build/odin
RUN chown -R user /home/user/
USER user
WORKDIR /home/user/build/odin
RUN python3 -m venv venv
RUN mkdir /home/user/projects
ENV PATH="/home/user/build/odin/venv/bin:$PATH"
RUN pip3 install -r requirements.txt
RUN pip3 install -e .
VOLUME /home/user/projects
