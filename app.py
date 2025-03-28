from flask import Flask, render_template
import subprocess
import re

app = Flask(__name__)

def get_networks():
    try:
        result = subprocess.run(['netsh', 'wlan', 'show', 'network'], capture_output=True, text=True, check=True)
        output = result.stdout
        networks = re.findall(r'SSID \d+ : (.*)', output)
        return networks
    except subprocess.CalledProcessError as e:
        print(f"Error fetching networks: {e}")
        return []

def get_network_password(network_name):
    try:
        result = subprocess.run(['netsh', 'wlan', 'show', 'profile', network_name, 'key=clear'], capture_output=True, text=True, check=True)
        output = result.stdout
        password = re.search(r'Key Content\s+:\s+(.*)', output)
        if password:
            return password.group(1)
        else:
            return "Password not found"
    except subprocess.CalledProcessError as e:
        return f"Error fetching password for {network_name}: {e}"

@app.route('/')
def index():
    networks = get_networks()
    network_info = []
    if networks:
        for network in networks:
            password = get_network_password(network)
            network_info.append((network, password))
    
    # Passing the network_info list to the template
    return render_template('index.html', network_info=network_info)

if __name__ == "__main__":
    app.run(debug=True)
