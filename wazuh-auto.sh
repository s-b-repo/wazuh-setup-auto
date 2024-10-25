#!/bin/bash

# Check if script is run as root
if [ "$EUID" -ne 0 ]; then 
  echo "Please run as root"
  exit
fi

# Prompt for Wazuh Dashboard credentials
echo "Please enter the credentials for the Wazuh Dashboard."
read -p "Username: " dashboard_username
read -sp "Password: " dashboard_password
echo

# Prompt for the server's IP address
echo "Enter the IP address of the server. This IP address will be used to access the Wazuh Dashboard."
read -p "Server IP Address: " server_ip

# Update system
echo "Updating system..."
apt update && apt upgrade -y

# Install required dependencies
echo "Installing dependencies..."
apt install -y curl apt-transport-https software-properties-common lsb-release gnupg

# Install Wazuh repository GPG key and repository
echo "Setting up Wazuh repository..."
curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | apt-key add -
echo "deb https://packages.wazuh.com/4.x/apt/ stable main" | tee /etc/apt/sources.list.d/wazuh.list

# Install the Wazuh Manager
echo "Installing Wazuh Manager..."
apt update && apt install -y wazuh-manager

# Enable and start Wazuh Manager
systemctl daemon-reload
systemctl enable wazuh-manager
systemctl start wazuh-manager

# Install Wazuh Indexer
echo "Installing Wazuh Indexer..."
curl -s https://packages.elastic.co/GPG-KEY-elasticsearch | apt-key add -
echo "deb https://packages.elastic.co/elasticsearch/7.x/debian stable main" | tee -a /etc/apt/sources.list.d/elastic-7.x.list
apt update && apt install -y opensearch

# Enable and start Wazuh Indexer
systemctl enable opensearch
systemctl start opensearch

# Configure Opensearch for Wazuh
echo "Configuring Wazuh Indexer..."
curl -X PUT "localhost:9200/_cluster/settings" -H 'Content-Type: application/json' -d'{
  "persistent": {
    "cluster.routing.allocation.disk.watermark.low": "1gb",
    "cluster.routing.allocation.disk.watermark.high": "500mb",
    "cluster.routing.allocation.disk.watermark.flood_stage": "100mb",
    "cluster.info.update.interval": "1m"
  }
}'

# Install Wazuh Dashboard
echo "Installing Wazuh Dashboard..."
apt install -y wazuh-dashboard

# Enable and start Wazuh Dashboard
systemctl daemon-reload
systemctl enable wazuh-dashboard
systemctl start wazuh-dashboard

# Set up Wazuh Dashboard credentials
echo "Setting Wazuh Dashboard credentials..."
curl -X POST "http://localhost:55000/api/v1/security/user" -H "Authorization: Basic YWRtaW46YWRtaW4=" -H "Content-Type: application/json" -d "{
  \"username\": \"$dashboard_username\",
  \"password\": \"$dashboard_password\",
  \"role\": \"admin\"
}"

# Configure Filebeat for Wazuh
echo "Configuring Filebeat..."
apt install -y filebeat
filebeat modules enable wazuh
sed -i 's|localhost:9200|http://localhost:9200|' /etc/filebeat/filebeat.yml

# Enable and start Filebeat
systemctl daemon-reload
systemctl enable filebeat
systemctl start filebeat

# Print final instructions
echo -e "\nWazuh installation and configuration complete."
echo "Access the Wazuh Dashboard at http://${server_ip}:5601 with the provided credentials."
echo -e "Username: ${dashboard_username}"
echo -e "Password: ${dashboard_password}"
