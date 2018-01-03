FROM eclipse/ubuntu_python

ENV LANG=C.UTF-8 \
    DOCKER_VERSION=1.6.0 \
    DOCKER_BUCKET=get.docker.com

RUN sudo apt-get install -y git && \
    sudo apt-get install -y curl && \
    sudo curl -sSL "https://${DOCKER_BUCKET}/builds/Linux/x86_64/docker-${DOCKER_VERSION}" -o /usr/bin/docker && \
    sudo chmod 755 /usr/bin/docker && \
    cd ~ && \
    git clone https://github.com/tengu-team/tengu-cli.git && \
    cd tengu-cli/ && \
    git checkout no-kubectl && \
    sudo pip install -e . && \
    sudo mkdir -p /projects

WORKDIR /projects
