import os
import subprocess
import sys
import argparse

def run_command(command, shell=False):
    """Runs a command and prints its output."""
    try:
        if shell:
            process = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        else:
            process = subprocess.run(command.split(), check=True, text=True, capture_output=True)
        print(process.stdout)
        with open("wazuh_setup.log", "a") as log_file:
            log_file.write(process.stdout)
            log_file.write(process.stderr)
        return process.stdout
    except subprocess.CalledProcessError as e:
        with open("wazuh_setup.log", "a") as log_file:
            log_file.write(f"Error: {e.stderr}")
        print(f"Error: {e.stderr}")
        sys.exit(1)

def install_prerequisites():
    """Installs prerequisites for Wazuh."""
    print("Installing prerequisites...")
    os_type = run_command("grep '^ID=' /etc/os-release | cut -d= -f2 | tr -d '\"'").strip()
    if os_type in ["ubuntu", "debian"]:
        run_command("sudo apt-get update")
        run_command("sudo apt-get install -y curl apt-transport-https software-properties-common")
    elif os_type in ["centos", "rhel"]:
        run_command("sudo yum install -y curl policycoreutils-python-utils")
    else:
        print(f"Unsupported OS detected: {os_type}. Supported: Ubuntu, Debian, CentOS, RHEL.")
        sys.exit(1)

def install_wazuh_manager():
    """Installs Wazuh Manager."""
    print("Installing Wazuh Manager...")
    try:
        run_command("curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | sudo apt-key add -")
    except subprocess.CalledProcessError:
        print("Failed to add Wazuh GPG key. Check your network connection and try again.")
        sys.exit(1)

    run_command('echo "deb https://packages.wazuh.com/4.x/apt/ stable main" | sudo tee /etc/apt/sources.list.d/wazuh.list')
    run_command("sudo apt-get update")
    run_command("sudo apt-get install -y wazuh-manager")

def configure_wazuh_manager(password):
    """Configures Wazuh Manager registration password."""
    print("Configuring Wazuh Manager...")
    config_file = "/var/ossec/etc/ossec.conf"
    backup_file = f"{config_file}.bak"
    try:
        run_command(f"sudo cp {config_file} {backup_file}")
        with open(config_file, "r") as file:
            config = file.read()

        config = config.replace("<key>your_registration_password</key>", f"<key>{password}</key>")

        with open(config_file, "w") as file:
            file.write(config)

        run_command("sudo systemctl restart wazuh-manager")
    except Exception as e:
        print(f"Failed to configure Wazuh Manager: {e}")
        sys.exit(1)

def setup_wazuh_api(password):
    """Sets up Wazuh API user and password."""
    print("Setting up Wazuh API...")
    try:
        run_command(f"sudo /var/ossec/framework/python/bin/python3 /var/ossec/api/scripts/configure_api.py -u wazuh -p {password}")
        run_command("sudo systemctl restart wazuh-api")
    except Exception as e:
        print(f"Failed to set up Wazuh API: {e}")
        sys.exit(1)

def validate_password(password):
    """Validates the password for minimum requirements."""
    if len(password) < 8:
        print("Error: Password must be at least 8 characters long.")
        sys.exit(1)

def main():
    """Main function to automate Wazuh Manager setup."""
    print("Wazuh Manager Installer")

    # Parse arguments for non-interactive setup
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration-password", required=False, help="Registration password for agents.")
    parser.add_argument("--api-password", required=False, help="Password for Wazuh API user.")
    args = parser.parse_args()

    # Step 1: Install prerequisites
    install_prerequisites()

    # Step 2: Install Wazuh Manager
    install_wazuh_manager()

    # Step 3: Configure Wazuh Manager registration password
    reg_password = args.registration_password or input("Enter a registration password for agents: ").strip()
    validate_password(reg_password)
    configure_wazuh_manager(reg_password)

    # Step 4: Configure API
    api_password = args.api_password or input("Enter a password for the Wazuh API user: ").strip()
    validate_password(api_password)
    setup_wazuh_api(api_password)

    print("Wazuh Manager installation and setup complete!")
    print("You can now manage Wazuh using the API or via the dashboard.")

if __name__ == "__main__":
    main()
