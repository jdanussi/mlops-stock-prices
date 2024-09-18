
# 

cd /path/to/project-folder
source setup.sh
pipenv install --dev
pipenv shell


## Boostrap 1

- pausar todos los Dags, eliminar corridas anteriores
- zapear todas las tablas de la db stocks
- desde el notebook 'test_xgboost.ipynb' bajar goog periodo 2024-01-01 al 2024-06-28 y meterlo en tabla 'stock_ohlc'
- desde el notebook 'test_xgboost.ipynb' calcular las predicciones para ese data de referencia, usando el modelo productivo de S3. Guardar el dataset con la sequence y las pedicciones en tabla 'stock_predictions'
- despausar dag data_ingest y dejar que corra el cathup asi completa las bajadas y forecasting desde 2024-07-01 al dia de hoy
- despausar el dag de monitoria para que corran las metricas evidently que estan seteadas con catchup. Corren los viernes por tanto deben generar los 4 puntos de 2024-07 y algunos puntos más de 2024-08.


## Boostrap 2

- pausar todos los dags, eliminar corridas anteriores
- zapear todas las tablas de la db stocks
- desde el notebook 'test_xgboost.ipynb' bajar goog periodo 2024-01-01 al 2024-06-28 y meterlo en tabla 'stock_ohlc'
- desde airflow correr manuamente el dag de training para registrar en S3 un modelo productivo entrenado con ese dataset
- desde el notebook 'test_xgboost.ipynb' calcular las predicciones para ese data de referencia, usando el modelo productivo de S3 registrado en el punto anterior. Guardar el dataset con la sequence y las pedicciones en tabla 'stock_prediction'
- despausar dag data_ingest y dejar que corra el cathup hasta el end date 07-Jul-2024 (domingo): tiene que correr 5 veces.
- despausar dag de model_monitoring y dejar que corra el cathup hasta el end date 07-Jul-2024 (domingo): tiene que correr 1 vez.
- despausar dag de model_training y dejar que corra el cathup hasta el end date 07-Jul-2024 (domingo): no tiene que correr porque corre cada 14 días

ir corriendo el end_date usando los domingos como limites de periodos de 1 semana
14-jul
21-jul
28-jul
04-ago
11-ago
18-ago
now



EC2_SSH_KEY
HOST_DNS = ec2-xx-xxx-xxx-xxx.us-west-2.compute.amazonaws.com. (sale de Terraform)
USERNAME = ubuntu
TARGET_DIR = /home/ubuntu/app
AWS_ACCESS_KEY_ID = AKIAYG23TRVO3X6X46SB
AWS_SECRET_ACCESS_KEY = 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>
AWS_BUCKET


ssh-keygen -t ed25519
~/.ssh/mlopskey.pub

ssh-keygen -t ed25519
Generating public/private ed25519 key pair.
Enter file in which to save the key (/home/jdanussi/.ssh/id_ed25519): mlopskey
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in mlopskey
Your public key has been saved in mlopskey.pub
The key fingerprint is:
SHA256:/ch++BPpSGBnjhJSgQTx/mHH+auYJkIvRm3x4TBBknM jdanussi@jad-xps15
The key's randomart image is:
+--[ED25519 256]--+
|  +*o...         |
|  ooE .          |
|   o.o           |
|   .= o.ooo      |
|   ..Bo+S*.  .   |
|  o oo+o.oooo    |
| o o  .. .++..   |
|  + o .o .o.+    |
| . o oo ..oo..   |
+----[SHA256]-----+

ls -ltr
total 156
-rw-r--r-- 1 jdanussi jdanussi   100 mar 24  2023 id_ed25519.pub
-rw------- 1 jdanussi jdanussi   411 mar 24  2023 id_ed25519
-rw-r--r-- 1 jdanussi jdanussi   390 ago 21  2023 gcp.pub
-rw------- 1 jdanussi jdanussi  1811 ago 21  2023 gcp
-rw-r--r-- 1 jdanussi jdanussi   744 ene 28  2024 id_rsa_argocd.pub
-rw------- 1 jdanussi jdanussi  3381 ene 28  2024 id_rsa_argocd
-rw------- 1 jdanussi jdanussi  1678 may 13 20:19 mlops-zoomcamp.pem
-rw------- 1 jdanussi jdanussi 55142 sep  2 15:31 known_hosts.old
-rw------- 1 jdanussi jdanussi 55978 sep  2 15:31 known_hosts
-rw------- 1 jdanussi jdanussi  4975 sep 12 09:26 config
-rw-r--r-- 1 jdanussi jdanussi   100 sep 12 20:25 mlopskey.pub
-rw------- 1 jdanussi jdanussi   411 sep 12 20:25 mlopskey





ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server

terraform init
terraform fmt
terraform plan
terraform apply / terraform apply -auto-approve



EC2_SSH_KEY

> cat ~/.ssh/mlopskey
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACDQQjZ5vLjluGrSRUws23CgKXNx4jAu2cElAJTkNS1HwQAAAJi6803buvNN
2wAAAAtzc2gtZWQyNTUxOQAAACDQQjZ5vLjluGrSRUws23CgKXNx4jAu2cElAJTkNS1HwQ
AAAEDoHBQeakAfy4zqUrVpVr3rrMT+lioNPJwsk3Zi0LxVT9BCNnm8uOW4atJFTCzbcKAp
c3HiMC7ZwSUAlOQ1LUfBAAAAEmpkYW51c3NpQGphZC14cHMxNQECAw==
-----END OPENSSH PRIVATE KEY-----
> cat ~/.ssh/mlopskey.pub 
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINBCNnm8uOW4atJFTCzbcKApc3HiMC7ZwSUAlOQ1LUfB jdanussi@jad-xps15
> 

appleboy/scp-action@master Error: missing server host


HOST_DNS=ec2-18-208-231-130.compute-1.amazonaws.com

USERNAME
ubuntu

TARGET_DIR
/home/ubuntu/app
/home/ubuntu/mlops-stock-prices


AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY





ubuntu@ip-10-0-1-92:~/.ssh$ cat authorized_keys 
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINBCNnm8uOW4atJFTCzbcKApc3HiMC7ZwSUAlOQ1LUfB mlopskey

HOST_DNS=ec2-54-85-41-86.compute-1.amazonaws.com; ssh -i ~/.ssh/mlopskey ubuntu@$HOST_DNS



      - name: Set environment variables
        run: |
          echo "HOST=${{ secrets.HOST_DNS }}" >> $GITHUB_ENV
          echo "USERNAME=${{ secrets.USERNAME }}" >> $GITHUB_ENV
          echo "PORT=22" >> $GITHUB_ENV
          echo "TARGET=${{ secrets.TARGET_DIR }}" >> $GITHUB_ENV

          # Handle the SSH key separately
          echo "${{ secrets.EC2_SSH_KEY }}" > private_key.pem
          chmod 600 private_key.pem
        shell: bash

      - name: Copy 'dags' folder
        uses: appleboy/scp-action@master
        with:
          host: ${{ env.HOST }}
          username: ${{ env.USERNAME }}
          port: ${{ env.PORT }}
          key: private_key.pem
          source: "./dags"
          target: ${{ env.TARGET }}


sudo apt-get update
sudo apt install postgresql-client-common
sudo apt install postgresql
