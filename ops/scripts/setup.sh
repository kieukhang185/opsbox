#!/bin/bash

get_sys_name(){
    PRETTY_NAME=$(cat /etc/*-release | grep "PRETTY_NAME" | sed 's/PRETTY_NAME=//g' | sed 's/"//g')
    echo "${PRETTY_NAME}" | awk -F ' ' '{print $1}'
}

cmd_check(){ command -v "$1" &> /dev/null; }

require_pkgs() {
  sudo apt-get update -y
  sudo apt-get install -y ca-certificates curl gnupg lsb-release
}

### --- Function to install Docker ---
install_docker() {
    sys=$(get_sys_name)
    if [[ "${sys,,}" == "ubuntu" || "${sys,,}" == "debian" ]]; then
        echo "⚡ Installing Docker for ${sys}..."
        sudo apt-get update -y
        sudo apt-get install -y \
            ca-certificates \
            gnupg \
            lsb-release

        # Add Docker’s official GPG key
        sudo mkdir -p /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/"${sys}"/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

        # Set up the repository
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/'${sys}' \
        $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

        sudo apt-get update -y
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

        # Enable and start Docker
        sudo systemctl enable docker
        sudo systemctl start docker
        sudo usermod -aG docker "${USER}"
        newgrp docker

        cmd_check docker && echo "✅ Docker installed successfully: $(docker --version)" || echo "Docker installation failed"
    else
        echo "Unsupported system: ${sys}. Exiting."
        exit 1
    fi

}

ensure_docker(){
    if cmd_check docker
    then
        echo "✅ Docker present: $(docker --version)"
    else
        install_docker
    fi
}

install_kubectl(){
    echo "⚡ Installing Kubectl..."
    sudo snap install kubectl --classic
    cmd_check kubectl && echo "✅ Kubectl installed successfully: $(kubectl version --client)" || echo "Kubectl installation failed"
}

ensure_kubectl(){
    if cmd_check kubectl
    then
        echo "✅ kubectl present: $(kubectl version --client)"
    else
        install_kubectl
    fi
}

### --- Function to install Kind ---
install_kind() {
    echo "⚡ Installing Kind..."
    KIND_VERSION="v0.23.0"  # change if needed
    curl -Lo ./kind "https://kind.sigs.k8s.io/dl/${KIND_VERSION}/kind-linux-amd64"
    chmod +x ./kind
    sudo mv ./kind /usr/local/bin/kind
    cmd_check kind &&  echo "✅ Kind installed successfully: $(kind --version)" ||  echo "Kind installation failed"
    echo "✅ Kind installed successfully: $(kind --version)"
}

ensure_kind(){
    if cmd_check kind
    then
        echo "✅ Kind present: $(kind --version)"
    else
        install_kind
    fi
}

install_helm(){
    echo "⚡ Installing Helm..."
    sudo snap install helm --classic
    cmd_check helm && echo "✅ Helm installed successfully: $(helm version --shortt)" || echo "Helm installation failed"
}

ensure_helm(){
    if cmd_check helm
    then
        echo "✅ Helm present: $(helm version --short)"
    else
        install_helm
    fi
}

setup_k8s_tools(){
    echo "Setting up Kubernetes tools..."
    ensure_docker
    ensure_kubectl
    ensure_kind
    ensure_helm
}

setup_pre_commit(){
    sudo apt install -y pre-commit
    pre-commit install
    pre-commit run --all-file
}

setup(){
    echo "Setting up..."
    sys=$(get_sys_name)
    if [[ "${sys}" == "Ubuntu" || "${sys}" == "Debian" ]]; then
        require_pkgs
        setup_k8s_tools
    fi
}