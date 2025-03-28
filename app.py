from flask import Flask, render_template, request, jsonify
import requests
import socket
import os
from datetime import datetime

app = Flask(__name__)


@app.route("/")
def home():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return render_template("home.html", hostname=hostname, ip_address=ip_address)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/test-connectivity", methods=["GET", "POST"])
def test_connectivity():
    if request.method == "POST":
        target_ip = request.form.get("target_ip")
        protocol = request.form.get("protocol", "http")
        port = request.form.get("port", 80)
        endpoint = request.form.get("endpoint", "/")
        
        url = f"{protocol}://{target_ip}:{port}{endpoint}"
        result = {}
        result["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result["hostname"] = socket.gethostname()
        result["source_ip"] = socket.gethostbyname(socket.gethostname())
        result["target_ip"] = target_ip
        result["url_tested"] = url
        
        try:
            response = requests.get(url, timeout=5)
            result["status_code"] = response.status_code
            result["success"] = response.status_code < 400
            result["response_time"] = response.elapsed.total_seconds()
            
            # Only include response text if it's not too large
            if len(response.text) < 1000:
                result["response_text"] = response.text
            else:
                result["response_text"] = response.text[:500] + "... (truncated)"
                
        except requests.exceptions.RequestException as e:
            result["success"] = False
            result["error"] = str(e)
        
        return render_template("connectivity_result.html", result=result)
    
    return render_template("test_connectivity.html")


@app.route("/api/server-info")
def server_info():
    """API endpoint returning information about this server"""
    info = {
        "timestamp": datetime.now().isoformat(),
        "hostname": socket.gethostname(),
        "ip_address": socket.gethostbyname(socket.gethostname()),
        "platform": os.name,
        "environment": os.environ.get("FLASK_ENV", "development")
    }
    return jsonify(info)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
