#!/usr/bin/env python3
import os
import subprocess
import getpass
import sys
import socket

def run_command(command, check=True, shell=False):
    """Run a shell command and handle errors."""
    try:
        result = subprocess.run(command, check=check, shell=shell, text=True, capture_output=True)
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        print(f"Error running command {' '.join(command) if not shell else command}: {e.stderr}")
        return None, e.stderr

def check_root():
    """Check if script is running with sudo privileges."""
    if os.geteuid() != 0:
        print("This script requires sudo privileges. Please run with sudo.")
        sys.exit(1)

def setup_ssh():
    """Set up SSH server and configure static IP."""
    print("Setting up SSH...")
    # Install openssh-server
    run_command(["apt", "update"])
    stdout, stderr = run_command(["apt", "install", "-y", "openssh-server"])
    if stderr and "already the newest version" not in stderr:
        print("Failed to install openssh-server.")
        return False

    # Enable and start SSH
    run_command(["systemctl", "enable", "ssh"])
    run_command(["systemctl", "start", "ssh"])

    # Get IP address
    ip_address = socket.gethostbyname(socket.gethostname())
    if not ip_address.startswith("192.168") and not ip_address.startswith("10."):
        ip_address = subprocess.run("ip addr show | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}' | cut -d'/' -f1", shell=True, text=True, capture_output=True).stdout.strip()

    # Prompt for static IP (optional)
    use_static_ip = input("Do you want to set a static IP for the Raspberry Pi? (y/n): ").lower() == 'y'
    if use_static_ip:
        static_ip = input("Enter static IP (e.g., 192.168.1.100): ")
        gateway = input("Enter gateway IP (e.g., 192.168.1.1): ")
        netplan_config = f"""
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      dhcp4: no
      addresses:
        - {static_ip}/24
      gateway4: {gateway}
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
"""
        with open("/etc/netplan/01-netcfg.yaml", "w") as f:
            f.write(netplan_config)
        run_command(["netplan", "apply"])
        print(f"Static IP set to {static_ip}")

    print(f"SSH is enabled. Raspberry Pi IP: {ip_address}")
    return ip_address

def setup_jupyter():
    """Install and configure Jupyter Notebook."""
    print("Setting up Jupyter Notebook...")
    # Install Python and pip
    run_command(["apt", "install", "-y", "python3-pip", "python3-dev"])

    # Install Jupyter
    run_command(["pip3", "install", "--user", "jupyter"])

    # Add pip to PATH
    home_dir = os.path.expanduser("~")
    bashrc_path = os.path.join(home_dir, ".bashrc")
    with open(bashrc_path, "a") as f:
        f.write('\nexport PATH="$HOME/.local/bin:$PATH"\n')
    os.system(f"source {bashrc_path}")

    # Generate Jupyter config
    run_command(["/home/ubuntu/.local/bin/jupyter", "notebook", "--generate-config"])

    # Configure Jupyter for remote access
    jupyter_config = os.path.join(home_dir, ".jupyter", "jupyter_notebook_config.py")
    port = input("Enter Jupyter port (default 8889): ") or "8889"
    config_content = f"""
c.NotebookApp.ip = '0.0.0.0'
c.NotebookApp.port = {port}
c.NotebookApp.open_browser = False
"""
    with open(jupyter_config, "a") as f:
        f.write(config_content)

    # Set Jupyter password
    print("Set a password for Jupyter Notebook.")
    run_command(["/home/ubuntu/.local/bin/jupyter", "notebook", "password"])

    # Start Jupyter in background
    run_command([f"nohup /home/ubuntu/.local/bin/jupyter notebook --no-browser --port={port} &"], check=False)
    print(f"Jupyter Notebook started on port {port}")
    return port

def setup_shared_directory():
    """Create a shared directory for scripts."""
    shared_dir = "/home/ubuntu/shared"
    run_command(["mkdir", "-p", shared_dir])
    run_command(["chmod", "777", shared_dir])
    print(f"Shared directory created at {shared_dir}")

def print_student_instructions(ip_address, jupyter_port):
    """Print instructions for students to connect and run scripts."""
    print("\n=== Instructions for Students ===")
    print(f"1. **SSH Access**:")
    print(f"   - Run: ssh ubuntu@{ip_address}")
    print(f"   - Use the provided credentials or SSH key.")
    print(f"2. **Jupyter Notebook Access**:")
    print(f"   - Create SSH tunnel: ssh -N -L localhost:8888:localhost:{jupyter_port} ubuntu@{ip_address}")
    print(f"   - Open browser: http://localhost:8888")
    print(f"   - Enter the Jupyter password set earlier.")
    print(f"3. **Running Scripts**:")
    print(f"   - **Local Execution**: Copy your script (e.g., script.py) to your local machine and run:")
    print(f"       python3 script.py")
    print(f"   - **Remote Execution on Raspberry Pi**:")
    print(f"       - Copy script to Raspberry Pi: scp script.py ubuntu@{ip_address}:/home/ubuntu/shared/")
    print(f"       - Run remotely: ssh ubuntu@{ip_address} 'python3 /home/ubuntu/shared/script.py'")
    print(f"   - **Jupyter Execution**: Upload script.py to /home/ubuntu/shared, then run in Jupyter Notebook.")
    print(f"4. **Sample Script for Testing**:")
    print(f"   Create a file `script.py` with:")
    print(f"   ```python")
    print(f"   import platform")
    print(f"   print('Hello from', platform.node())")
    print(f"   ```")
    print(f"   Run locally and remotely to see different outputs.")

def main():
    """Main function to set up Raspberry Pi and guide students."""
    check_root()
    print("Setting up Raspberry Pi for remote access and script execution...")

    # Setup SSH
    ip_address = setup_ssh()
    if not ip_address:
        print("Failed to set up SSH. Exiting.")
        sys.exit(1)

    # Setup Jupyter Notebook
    jupyter_port = setup_jupyter()

    # Setup shared directory
    setup_shared_directory()

    # Print instructions for students
    print_student_instructions(ip_address, jupyter_port)

    print("\nSetup complete! Students can now connect and run scripts.")

if __name__ == "__main__":
    main()
