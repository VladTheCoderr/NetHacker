from flask import Flask, render_template, send_file
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

def save_to_file(data, filename='network_passwords.txt'):
    try:
        with open(filename, 'w') as file:
            file.write(data)
    except Exception as e:
        print(f"Error saving to file: {e}")

@app.route('/')
def home():
    networks = get_networks()
    network_info = []
    if networks:
        for network in networks:
            password = get_network_password(network)
            network_info.append((network, password))
        output = "\n".join([f"- {network}: {password}" for network, password in network_info])
        save_to_file(output)
    else:
        network_info.append(("No networks found", ""))
    return render_template('index.html', network_info=network_info)

@app.route('/download')
def download_file():
    return send_file('network_passwords.txt', as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
