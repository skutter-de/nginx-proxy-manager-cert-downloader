# nginx Proxy Manager Cert Downloader

Download Certificates from nginx Proxy Manager via API. Set the following environment Variables:

| Variable                           | Description                                                                         |
| ---------------------------------- | ----------------------------------------------------------------------------------- |
| NGINX_PROXY_MANAGER_URL            | URL to the nginx Proxy Manager instance                                             |
| NGINX_PROXY_MANAGER_USERNAME       | Username                                                                            |
| NGINX_PROXY_MANAGER_PASSWORD       | Password                                                                            |
| NGINX_PROXY_MANAGER_CERT_NAME      | (Partial) name of your cert                                                         |
| NGINX_PROXY_MANAGER_FULLCHAIN_PATH | Path where the fullchain.pem should be stored                                       |
| NGINX_PROXY_MANAGER_PRIVKEY_PATH   | Path where the privkey.pem should be stored                                         |
| NGINX_PROXY_MANAGER_RESTART_UNIT   | systemd unit to be restarted after deployment (leave unset to not restart anything) |

## Setup

### Requirements

- Python 3.11

### Installation

1. Create a venv

```shell
python3.11 -m venv /var/lib/nginx-proxy-manager-cert-downloader/venv
```

2. Activate venv and install the package

```shell
source /var/lib/nginx-proxy-manager-cert-downloader/venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install nginx-proxy-manager-cert-downloader
```

3. Create file for environment variables

Open `/etc/sysconfig/cert-downloader`:

```shell
NGINX_PROXY_MANAGER_URL="https://proxy.example.com"
NGINX_PROXY_MANAGER_USERNAME="admin@example.com"
NGINX_PROXY_MANAGER_PASSWORD="supersecret"
NGINX_PROXY_MANAGER_CERT_NAME="myhost.example.com"
NGINX_PROXY_MANAGER_FULLCHAIN_PATH="/etc/pki/tls/certs/myhost.example.com.pem"
NGINX_PROXY_MANAGER_PRIVKEY_PATH="/etc/pki/tls/private/myhost.example.com.pem"
NGINX_PROXY_MANAGER_RESTART_UNIT="myserver.service"
```

4. Deploy systemd units

Timer (`/etc/systemd/system/cert-downloader.timer`):

```ini
[Unit]
Description=cert-downloader.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

Service (`/etc/systemd/system/cert-downloader.service`)

```ini
[Unit]
Description=Download certificate from nginx proxy manager
After=network.target
Wants=network-online.target

[Service]
Restart=no
Type=oneshot
ExecStart=/usr/local/bin/cert-downloader
EnvironmentFile=/etc/sysconfig/cert-downloader

[Install]
WantedBy=multi-user.target
```

5. Reload systemd an enable timer

```shell
systemctl daemon-reload
systemctl enable cert-downloader.timer
```

6. (optional) Run script manually

```shell
systemctl start cert-downloader.service
```
