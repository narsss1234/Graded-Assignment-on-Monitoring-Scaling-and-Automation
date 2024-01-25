#!/bin/bash

sudo apt update

sudo apt install awscli nginx -y

aws s3 cp s3://web-application-static-files-1/index.html /tmp/index.html

sudo systemctl start nginx

sudo systemctl enable nginx

sudo rm -rf /var/www/html/*

sudo cp /tmp/index.html /var/www/html/index.html

sudo systemctl restart nginx