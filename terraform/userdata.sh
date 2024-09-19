sudo apt-get update -y
sudo apt-get install docker.io -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ubuntu

DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
mkdir -p $DOCKER_CONFIG/cli-plugins
curl -SL https://github.com/docker/compose/releases/download/v2.29.4/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose

cd /home/ubuntu
mkdir mlops-stock-prices
sudo chmod -R 707 /home/ubuntu/mlops-stock-prices
echo 'export PATH="${HOME}/mlops-stock-prices:${PATH}"' >> .bashrc
source .bashrc

