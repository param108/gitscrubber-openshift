#! /bin/bash
CLIENT_ID=$1
CLIENT_SECRET=$2

echo "CLIENT_ID='${CLIENT_ID}'" >> myproject/settings.py
echo "CLIENT_SECRET='${CLIENT_SECRET}'" >> myproject/settings.py
