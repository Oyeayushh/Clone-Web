# clonemini

## Quick Start

### Prerequisites
- Python 3.8+
- MongoDB
- ImgBB API Key
- Telegram Bot Token

### Setup Commands

```bash
# Clone repository
git clone https://github.com/Oyeayushh/Clone-Web.git
cd Clone-Web

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from .env.example)
cp .env.example .env
# Edit .env with your credentials

# Run application
uvicorn main:app --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000` in your browser.

---

## VPS Deployment

### Production Setup

```bash
# SSH to VPS
ssh root@your_vps_ip

# Setup project
cd /home
git clone https://github.com/Oyeayushh/Clone-Web.git
cd Clone-Web
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Edit .env with your production credentials
nano .env

# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

### Setup Systemd Service (Auto-restart)

```bash
# Create service file
sudo nano /etc/systemd/system/clone-web.service
```

Paste this:
```ini
[Unit]
Description=Clone Web Application
After=network.target

[Service]
User=root
WorkingDirectory=/home/Clone-Web
Environment="PATH=/home/Clone-Web/venv/bin"
ExecStart=/home/Clone-Web/venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 main:app

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable clone-web
sudo systemctl start clone-web
```

### Setup Nginx Reverse Proxy

```bash
sudo apt install nginx -y
sudo nano /etc/nginx/sites-available/clone-web
```

Paste this:
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Then:
```bash
sudo ln -s /etc/nginx/sites-available/clone-web /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your_domain.com
```

---

## Useful Commands

```bash
# View logs
journalctl -u clone-web -f

# Restart service
sudo systemctl restart clone-web

# Stop service
sudo systemctl stop clone-web

# Check status
sudo systemctl status clone-web
```
