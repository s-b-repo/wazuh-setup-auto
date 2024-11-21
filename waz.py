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


def uninstall_wazuh():
    """Uninstalls Wazuh Manager and cleans up."""
    print("Uninstalling Wazuh Manager...")
    run_command("sudo apt-get purge -y wazuh-manager")
    run_command("sudo rm -rf /var/ossec")
    run_command("sudo apt-get autoremove -y")


def install_prerequisites():
    """Installs prerequisites for Wazuh."""
    print("Installing prerequisites...")
    run_command("sudo apt-get update")
    run_command("sudo apt-get install -y curl apt-transport-https software-properties-common")


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


def configure_firewall():
    """Configures the firewall to allow Wazuh ports."""
    print("Configuring firewall...")
    run_command("sudo ufw allow 1514")
    run_command("sudo ufw allow 1515")
    run_command("sudo ufw allow 55000")
    run_command("sudo ufw reload")


def main():
    """Main function to automate Wazuh Manager setup."""
    print("Wazuh Manager Installer & Reinstaller for Ubuntu")

    # Step 1: Uninstall Wazuh (if needed)
    uninstall_wazuh()

    # Step 2: Install prerequisites
    install_prerequisites()

    # Step 3: Install Wazuh Manager
    install_wazuh_manager()

    # Step 4: Configure Wazuh Manager registration password
    reg_password = input("Enter a registration password for agents: ")
    configure_wazuh_manager(reg_password)

    # Step 5: Configure Wazuh API
    api_password = input("Enter a password for the Wazuh API user: ")
    setup_wazuh_api(api_password)

    # Step 6: Configure Firewall
    configure_firewall()

    print("Wazuh Manager installation, reconfiguration, and setup complete!")
    print("You can now manage Wazuh using the API or via the dashboard.")
    print(f"Registration password for agents: {reg_password}")
    print(f"Wazuh API credentials - User: wazuh, Password: {api_password}")


if __name__ == "__main__":
    main()
