#!/bin/bash

get_sys_name(){
    PRETTY_NAME=$(cat /etc/*-release | grep "PRETTY_NAME" | sed 's/PRETTY_NAME=//g' | sed 's/"//g')
    echo "${PRETTY_NAME}" | awk -F ' ' '{print $1}'
}

cmd_check(){ command -v "$1" &> /dev/null; }

require_pkgs() {
  sudo apt-get update -y
  sudo apt-get install -y ca-certificates curl gnupg lsb-release make
}

### --- Function to install Docker ---
install_docker() {
    sys=$(get_sys_name)
    sys="${sys,,}"
    if [[ "${sys}" == "ubuntu" || "${sys}" == "debian" ]]; then
        echo "⚡ Installing Docker for ${sys}..."
        require_pkgs

        # Add Docker’s official GPG key
        sudo mkdir -p /etc/apt/keyrings
        curl -fsSL "https://download.docker.com/linux/${sys}/gpg" | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

        # Set up the repository
        echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/${sys} $(lsb_release -cs) stable" \
        | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

        sudo apt-get update -y
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin || true

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
    version="v1.33.4" # for same version at all
    # sudo apt-get install kubectl
    curl -LO "https://dl.k8s.io/release/${version}/bin/linux/amd64/kubectl"
    curl -LO "https://dl.k8s.io/release/${version}/bin/linux/amd64/kubectl.sha256"
    echo "$(cat kubectl.sha256) kubectl" | sha256sum --check
    chmod +x ./kubectl
    mkdir -pv /usr/local/bin
    sudo mv ./kubectl /usr/local/bin/kubectl
    export PATH=$PATH:/usr/local/bin/kubectl
    rm -rf kubectl kubectl.sha256

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
    KIND_VERSION="v0.30.0"  # change if needed
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
    # sudo snap install helm --classic
    helm_version="v3.17.4"
    tar_file="helm-${helm_version}-linux-amd64.tar.gz"
    wget https://get.helm.sh/${tar_file}
    tar -zxvf ${tar_file}
    sudo mv linux-amd64/helm /usr/local/bin/helm
    cmd_check helm && echo "✅ Helm installed successfully: $(helm version --short)" || echo "Helm installation failed"
}

ensure_helm(){
    if cmd_check helm
    then
        echo "✅ Helm present: $(helm version --short)"
    else
        install_helm
    fi
}

install_age(){
    echo "⚡ Installing Age..."
    age_version="v1.2.1"
    age_tar_file="age-${age_version}-linux-amd64.tar.gz"
    curl -LO "https://github.com/FiloSottile/age/releases/latest/download/age-${age_version}-linux-amd64.tar.gz"
    tar xf ${age_tar_file}
    sudo mv age/age age/age-keygen /usr/local/bin
    rm -rf age.tar.gz age ${age_tar_file}
    # sudo apt install -y age
    cmd_check age && echo "✅ Age installed successfully: $(age --version)" || echo "Age installation failed"
}

ensure_age(){
    if cmd_check age
    then
        echo "✅ Age present: $(age --version)"
    else
        install_age
    fi
}

install_sops(){
    echo "⚡ Installing SOPS..."
    sops_version="v3.10.2"
    sops_file="sops-${sops_version}.linux.amd64"
    curl -LO "https://github.com/getsops/sops/releases/download/${sops_version}/${sops_file}"
    chmod +x ${sops_file}
    sudo mv ${sops_file} /usr/local/bin/sops
    rm -rf ${sops_file}
    cmd_check sops && echo "✅ SOPS installed successfully: $(sops --version)" || echo "SOPS installation failed"
}

ensure_sops(){
    if cmd_check sops
    then
        echo "✅ SOPS present: $(sops --version)"
    else
        install_sops
    fi
}

install_python3_12_3(){
    python_version=3.12.3
    tar_file="Python-${python_version}.tar.xz"
    wget https://www.python.org/ftp/python/${python_version}/${tar_file}
    tar -xf "${tar_file}"
    cd Python-${python_version}
    /configure --enable-optimizations
    make -j $(nproc)
    sudo make altinstall
    sudo ln -sf $(which python3.12) /usr/bin/python3
    python3 --version
    sudo rm -rf ${tar_file} Python-${python_version}
}

secret_tool(){
    ensure_age
    ensure_sops
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
    require_pkgs
    setup_k8s_tools
    secret_tool
    cmd_check pre-commit || setup_pre_commit
}
