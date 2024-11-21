import os
import subprocess
import sys

def run_command(command, shell=False):
    """Runs a command and prints its output."""
    try:
        if shell:
            process = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        else:
            process = subprocess.run(command.split(), check=True, text=True, capture_output=True)
        print(process.stdout)
        return process.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        sys.exit(1)


def install_prerequisites():
    """Installs prerequisites for Wazuh."""
    print("Installing prerequisites...")
    os_type = run_command("grep '^ID=' /etc/os-release").strip()
    if "ubuntu" in os_type or "debian" in os_type:
        run_command("sudo apt-get update")
        run_command("sudo apt-get install -y curl apt-transport-https software-properties-common")
    elif "centos" in os_type or "rhel" in os_type:
        run_command("sudo yum install -y curl policycoreutils-python-utils")
    else:
        print("Unsupported OS. This script supports Ubuntu, Debian, CentOS, and RHEL.")
        sys.exit(1)


def install_wazuh_manager():
    """Installs Wazuh Manager."""
    print("Installing Wazuh Manager...")
    run_command("curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | sudo apt-key add -")
    run_command('echo "deb https://packages.wazuh.com/4.x/apt/ stable main" | sudo tee /etc/apt/sources.list.d/wazuh.list')
    run_command("sudo apt-get update")
    run_command("sudo apt-get install -y wazuh-manager")


def configure_wazuh_manager(password):
    """Configures Wazuh Manager registration password."""
    print("Configuring Wazuh Manager...")
    config_file = "/var/ossec/etc/ossec.conf"
    with open(config_file, "r") as file:
        config = file.read()

    config = config.replace("<key>your_registration_password</key>", f"<key>{password}</key>")

    with open(config_file, "w") as file:
        file.write(config)

    run_command("sudo systemctl restart wazuh-manager")


def setup_wazuh_api(password):
    """Sets up Wazuh API user and password."""
    print("Setting up Wazuh API...")
    run_command(f"sudo /var/ossec/framework/python/bin/python3 /var/ossec/api/scripts/configure_api.py -u wazuh -p {password}")
    run_command("sudo systemctl restart wazuh-api")


def main():
    """Main function to automate Wazuh Manager setup."""
    print("Wazuh Manager Installer")

    # Step 1: Install prerequisites
    install_prerequisites()

    # Step 2: Install Wazuh Manager
    install_wazuh_manager()

    # Step 3: Configure Wazuh Manager registration password
    reg_password = input("Enter a registration password for agents: ")
    configure_wazuh_manager(reg_password)

    # Step 4: Configure API
    api_password = input("Enter a password for the Wazuh API user: ")
    setup_wazuh_api(api_password)

    print("Wazuh Manager installation and setup complete!")
    print("You can now manage Wazuh using the API or via the dashboard.")

if __name__ == "__main__":
    main()
