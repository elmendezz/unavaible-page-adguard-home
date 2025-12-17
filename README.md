# 🛡️ AdGuard Home – Block Page Proxy

This project provides a **lightweight reverse proxy server written in Python**.  
It allows you to display a **custom and elegant block page** for **AdGuard Home** users.

It is ideal for users running AdGuard Home on:
- Raspberry Pi
- VPS
- Local servers
- Android (via Termux)

Instead of showing a generic connection error, blocked requests are redirected to a clean and user-friendly interface.

---

## 📋 Table of Contents

- ⚙️ How It Works
- 🧩 The Server Script (`run.py`)
- 🚀 Installation and Auto-Start
- 🛠️ AdGuard Home Configuration
- ❓ Troubleshooting

---

## ⚙️ How It Works

1. AdGuard Home blocks a domain (e.g. `ads.google.com`).
2. Instead of dropping the packet, AdGuard redirects the request to your **local IP address**.
3. The Python script intercepts the request on **port 80**.
4. It fetches the block page content hosted on a remote service (Vercel, Netlify, etc.).
5. The page is served to the user's browser while **preserving the original URL path**.

🚀 Result: a clean, professional blocking experience.

---

## 🧩 1. The Server Script (`run.py`)

Create a file named `run.py` and paste the following code.  
This script acts as a bridge between your local network and the hosted block page.

```python
import http.server
import socketserver
import urllib.request
import urllib.error

# --- CONFIGURATION ---
PORT = 80
# Exact URL of your hosted block page (Vercel, Netlify, etc.)
TARGET_URL = "https://unavaible-page-adguard-home.vercel.app"

class ReverseProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_proxy()

    def do_POST(self):
        self.handle_proxy()

    def handle_proxy(self):
        try:
            destination_url = TARGET_URL + self.path
            print(f"[Proxy] Requesting: {destination_url}")

            req = urllib.request.Request(destination_url)
            req.add_header('User-Agent', 'Mozilla/5.0')

            with urllib.request.urlopen(req) as response:
                self.send_response(response.getcode())

                for key, value in response.info().items():
                    if key.lower() == "content-type":
                        self.send_header(key, value)

                self.end_headers()
                self.wfile.write(response.read())

        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.end_headers()
        except Exception as e:
            print(f"[ERROR] {e}")
            self.send_response(500)
            self.end_headers()

# --- START SERVER ---
socketserver.TCPServer.allow_reuse_address = True

try:
    with socketserver.TCPServer(("", PORT), ReverseProxyHandler) as httpd:
        print(f"Reverse proxy running at http://localhost:{PORT}")
        print(f"Serving content from: {TARGET_URL}")
        httpd.serve_forever()
except PermissionError:
    print("Port 80 requires root/administrator privileges.")
except KeyboardInterrupt:
    print("Server stopped by user.")
```
## 🚀 2. Installation and Auto-Start

Choose your operating system to configure the proxy and start it automatically.

---

### 🐧 Option A: Linux (Systemd) — Recommended

Ideal for Raspberry Pi, Ubuntu, Debian, and headless servers.

#### 1️⃣ Move the script to a permanent location

```bash
sudo mkdir -p /opt/adguard-proxy
sudo cp run.py /opt/adguard-proxy/run.py
```

#### 2️⃣ Create the systemd service

```bash
sudo nano /etc/systemd/system/adguard-proxy.service
```

Paste the following content  
(`User=root` is required because port 80 needs elevated privileges):

```ini
[Unit]
Description=AdGuard Home Block Page Proxy
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/adguard-proxy
ExecStart=/usr/bin/python3 /opt/adguard-proxy/run.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

#### 3️⃣ Enable and start the service

```bash
sudo systemctl daemon-reload
sudo systemctl enable adguard-proxy
sudo systemctl start adguard-proxy
```

To check the status:

```bash
sudo systemctl status adguard-proxy
```

---

### 🪟 Option B: Windows

#### 1️⃣ Install Python

Install **Python 3** and make sure to check **Add Python to PATH** during installation.

#### 2️⃣ Manual execution (test)

Open **CMD or PowerShell** as **Administrator**, navigate to the script directory, and run:

```powershell
python run.py
```

You may see a Windows Firewall prompt.  
Allow access on **Private Networks**.

#### 3️⃣ Auto-start using Task Scheduler

1. Open **Task Scheduler**
2. Click **Create Task**
3. **General tab**
   - Name: `AdGuardProxy`
   - Check **Run with highest privileges**
4. **Triggers tab**
   - New → At system startup
5. **Actions tab**
   - Program/script: `pythonw.exe`
   - Arguments:
     ```
     C:\path\to\run.py
     ```

Reboot to test.

---

### 📱 Option C: Android (Termux)

> ⚠️ Requires **root access** or `tsu`, as Android without root cannot bind to port 80.

#### 1️⃣ Install dependencies

```bash
pkg install python tsu termux-boot
```

#### 2️⃣ Create the boot directory

```bash
mkdir -p ~/.termux/boot
```

#### 3️⃣ Create the startup script

```bash
nano ~/.termux/boot/start-proxy.sh
```

File contents:

```sh
#!/data/data/com.termux/files/usr/bin/sh

termux-wake-lock

sudo python /data/data/com.termux/files/home/run.py > /data/data/com.termux/files/home/proxy_log.txt 2>&1 &
```

#### 4️⃣ Make the script executable

```bash
chmod +x ~/.termux/boot/start-proxy.sh
```

#### 5️⃣ Enable auto-start

Open the **Termux:Boot** app once and reboot the device.

---

### 🍎 Option D: macOS

#### Manual execution

```bash
sudo python3 path/to/run.py
```

#### Auto-start (advanced)

Use **launchd** by creating a `.plist` file inside:

```bash
/Library/LaunchDaemons/
```

> ⚠️ macOS uses port 80 for Apache by default.  
> Make sure Apache is stopped if necessary:

```bash
sudo apachectl stop
```
