# clonemini

## 🚀 Deployment Guide - VPS Par Host Karne Ke Liye

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### VPS Setup Steps

#### 1. **SSH se VPS connect kro**
```bash
ssh root@your_vps_ip
```

#### 2. **System dependencies install kro**
```bash
apt update && apt upgrade -y
apt install python3-pip python3-venv git -y
```

#### 3. **Repository clone kro**
```bash
cd /home
git clone https://github.com/Oyeayushh/Clone-Web.git
cd Clone-Web
```

#### 4. **Virtual Environment banao**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 5. **Dependencies install kro**
```bash
pip install -r requirements.txt
```

#### 6. **Application run kro (Testing)**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Production Setup (Gunicorn + Nginx ke saath)

#### 1. **Gunicorn install kro**
```bash
pip install gunicorn
```

#### 2. **Systemd Service file banao** (`/etc/systemd/system/clone-web.service`)
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

#### 3. **Service enable aur start kro**
```bash
systemctl daemon-reload
systemctl enable clone-web
systemctl start clone-web
systemctl status clone-web
```

#### 4. **Nginx install aur configure kro**
```bash
apt install nginx -y
```

**Nginx Config** (`/etc/nginx/sites-available/clone-web`):
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 5. **Nginx enable kro**
```bash
ln -s /etc/nginx/sites-available/clone-web /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

#### 6. **SSL Certificate lao (Let's Encrypt)**
```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d your_domain.com
```

### Useful Commands

- **Logs dekhne ke liye:**
  ```bash
  journalctl -u clone-web -f
  ```

- **Service restart kro:**
  ```bash
  systemctl restart clone-web
  ```

- **Application stop kro:**
  ```bash
  systemctl stop clone-web
  ```

### Environment Variables
.env file create kro root directory mein agar zaroorat ho.

---

**Happy Hosting! 🎉**
