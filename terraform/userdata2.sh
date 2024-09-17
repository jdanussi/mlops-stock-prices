sudo apt-get update -y
sudo apt-get install docker.io -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ubuntu
cd /home/ubuntu
mkdir mlops-stock-prices
sudo chmod -R 707 /home/ubuntu/mlops-stock-prices
echo 'export PATH="${HOME}/mlops-stock-prices:${PATH}"' >> .bashrc
source .bashrc

