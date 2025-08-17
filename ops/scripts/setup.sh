#!/bin/bash

get_sys_name(){
    PRETTY_NAME=$(cat /etc/*-release | grep "PRETTY_NAME" | sed 's/PRETTY_NAME=//g' | sed 's/"//g')
    echo "${PRETTY_NAME}" | awk -F ' ' '{print $1}'
}

kubectl_install(){
    echo "Download the latest kubectl release"
    snap install kubectl --classic
}

kind_install(){
    curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64 # Adjust version as needed
    chmod +x ./kind
    sudo mv ./kind /usr/local/bin/kind
}

docker_install(){
    sys=$1
    sudo apt-get update
    sudo apt-get install -y docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker "${USER}"
    newgrp docker
}

setup(){
    echo "Setting up..."
    sys=$(get_sys_name)
    if [[ "$sys" == "Ubuntu" || "$sys" == "Debian" ]]; then
        sudo apt-get update && sudo apt-get upgrade -y
        sudo apt-get install -y curl
        docker || docker_install "${sys,,}"
    fi
}