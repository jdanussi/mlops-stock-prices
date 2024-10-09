#!/bin/bash

cd /tmp &&
echo "updating packages"
sudo yum update -y &&

echo "installing docker"
yum install -y docker
usermod -a -G docker ec2-user &&
systemctl enable --now docker &&
echo "vm.max_map_count=262144" >> /etc/sysctl.conf &&

echo "installing docker-compose"
curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose &&
chmod +x /usr/local/bin/docker-compose &&
echo "starting docker-compose"
sysctl -w vm.max_map_count=262144

echo "installing git"
yum install git -y &&

echo "logging into ec2-user to build mlflow"
sudo -u ec2-user -i <<'EOF'
pwd
whoami

echo "Connecting to my git remote repository and getting the docker-compose file for mlflow"
git init
touch linux-git-install.txt
git config --global init.defaultBranch "ec2-mlfow"
git config --global user.name "jdanussi"
git config --global user.email "jdanussi@gmail.com"
git add .
git commit -m "New linux git install commit"
git remote add main https://github.com/jdanussi/mlops-stock-prices.git
git remote update
git fetch
git checkout main/main docker-mlflow
git checkout main/main grafana
git checkout main/main docker-compose-mlflow.yaml
cp docker-compose-mlflow.yaml docker-compose.yaml

echo "building mlflow server"
echo -e "GF_SECURITY_ADMIN_PASSWORD=grafana" > .env
echo -e "AWS_ID=${AWS_ID}" >> .env
echo -e "AWS_KEY=${AWS_KEY}" >> .env
echo -e "DB_ENDPOINT=${DB_ENDPOINT}" >> .env
echo -e "DB_USER=mlflow" >> .env
echo -e "DB_PASS=mlflow" >> .env
echo -e "BACKEND_URI=postgresql://mlflow:mlflow@${DB_ENDPOINT}/mlflow" >> .env
echo -e ".idea/" > .gitignore
echo -e ".vscode-server/" >> .gitignore
echo -e ".env" >> .gitignore
echo -e "linux-git-install.txt" >> .gitignore
sudo chown -R ec2-user:ec2-user .

sudo chmod 666 /var/run/docker.sock
/usr/local/bin/docker-compose up -d

EOF
