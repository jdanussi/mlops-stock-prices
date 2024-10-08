#!/bin/bash

cd /tmp &&
echo "updating packages"
sudo yum update -y &&

echo "installing docker"
amazon-linux-extras install docker &&
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

echo "installing psql client"
sudo amazon-linux-extras install postgresql14 -y

echo "logging into ec2-user to build airflow"
sudo -u ec2-user -i <<'EOF'
pwd
whoami

echo "Connecting to my git remote repository and getting the docker-compose file for airflow"
git init
touch linux-git-install.txt
git config --global init.defaultBranch "ec2"
git config --global user.name "jdanussi"
git config --global user.email "jdanussi@gmail.com"
git add .
git commit -m "New linux git install commit"
git remote add develop https://github.com/jdanussi/mlops-stock-prices.git
git remote update
git fetch
git checkout develop/develop dags
git checkout develop/develop docker-airflow
git checkout develop/develop docker-postgres/init.sql
git checkout develop/develop docker-compose-prod.yaml
cp docker-compose-prod.yaml docker-compose.yaml

echo "building airflow client"
mkdir -p ./dags ./logs ./plugins ./models ./data ./reports
echo -e "AIRFLOW_UID=$(id -u)" > .env
echo -e "AIRFLOW_GID=0" >> .env
echo -e "AWS_ID=${AWS_ID}" >> .env
echo -e "AWS_KEY=${AWS_KEY}" >> .env
echo -e "DB_ENDPOINT=${DB_ENDPOINT}" >> .env
echo -e "DB_USER=airflow" >> .env
echo -e "DB_PASS=${db_password}" >> .env
echo -e "SQL_DB=airflow:${db_password}@${DB_ENDPOINT}/stocks" >> .env
echo -e ".idea/" > .gitignore
echo -e ".vscode-server/" >> .gitignore
echo -e ".env" >> .gitignore
echo -e "dags/" >> .gitignore
echo -e "logs/" >> .gitignore
echo -e "plugins/" >> .gitignore
echo -e "linux-git-install.txt" >> .gitignore
sudo chown -R ec2-user:ec2-user .

echo "creating databses, users and tables"
export PGPASSWORD=${db_password}
echo $PGPASSWORD
psql -h mlops-rds-instance.crcqa0ua6cb3.us-east-1.rds.amazonaws.com -U airflow -a -f docker-postgres/init.sql

sudo chmod 666 /var/run/docker.sock
/usr/local/bin/docker-compose up airflow-init
/usr/local/bin/docker-compose up -d

EOF