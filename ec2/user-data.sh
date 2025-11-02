#!/bin/bash
# EC2 user-data bootstrap script (for Ubuntu)
# Replace GIT_REPO with your repository clone URL (HTTPS). Example:
# GIT_REPO="https://github.com/youruser/website-monitoring-sample.git"

GIT_REPO="https://github.com/YOUR_USER/YOUR_REPO.git"
BRANCH="main"

# Update & install docker, docker-compose plugin
apt-get update -y
apt-get upgrade -y
apt-get install -y ca-certificates curl gnupg lsb-release git

# Install Docker
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add ubuntu user to docker group (optional)
usermod -aG docker ubuntu || true

# Clone repo and start docker compose
cd /home/ubuntu || cd /root
if [ -n "$GIT_REPO" ]; then
  git clone --branch "$BRANCH" "$GIT_REPO" app-monitor || true
  cd app-monitor || exit 0
  # Optionally copy config.example.env to .env and edit via cloud-init or SSH.
  docker compose up -d --build
fi

# End of user-data