Wazuh Installation Script

This script automates the installation and configuration of Wazuh Manager, Indexer (OpenSearch), and Wazuh Dashboard on Debian-based systems. It installs necessary dependencies, sets up repositories, configures services, and enables Filebeat for log management.

Overview

Wazuh is an open-source security monitoring platform. This script sets up the following components:

    Wazuh Manager: Manages Wazuh agents and performs data analysis.
    Wazuh Indexer: Stores security data (using OpenSearch).
    Wazuh Dashboard: Provides a web-based interface to visualize security data.
    Filebeat: Collects and forwards log data.

Prerequisites

    Operating System: Debian-based Linux distribution (e.g., Ubuntu)
    Root Privileges: This script requires root permissions.

Installation

    Clone the Repository:

    bash

git clone https://github.com/yourusername/wazuh-install-script.git
cd wazuh-install-script

Run the Script: Execute the script as root:

bash

    sudo ./install_wazuh.sh

Usage

The script will prompt for the following:

    Wazuh Dashboard Username: The username for accessing the Wazuh Dashboard.
    Wazuh Dashboard Password: The password for accessing the Wazuh Dashboard.
    Server IP Address: The IP address of the server where the Wazuh Dashboard is hosted.

Once these inputs are provided, the script will:

    Update the system and install dependencies.
    Add Wazuh and OpenSearch repositories.
    Install Wazuh Manager, Wazuh Indexer (OpenSearch), Wazuh Dashboard, and Filebeat.
    Configure OpenSearch index settings and Filebeat for log forwarding.
    Enable and start Wazuh and OpenSearch services.

Accessing the Dashboard

Once the installation completes, you can access the Wazuh Dashboard in your browser using the server IP address provided during setup.

text

http://<Server-IP>:5601

Log in with the credentials you specified during the installation process.
Contributing

Contributions are welcome! If you find an issue or want to add new features, feel free to submit a pull request.
