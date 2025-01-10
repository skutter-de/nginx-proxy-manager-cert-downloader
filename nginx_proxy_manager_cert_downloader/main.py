import os
import requests
import datetime

class NginxProxyManagerApi:
    base_url: str
    token: str
    token_expires: datetime.datetime
    headers: dict

    def __auth(self, refresh: bool = False, password: str = None):
        if refresh:
            resp = requests.get(f"{self.base_url}/tokens", headers=self.headers)
            self.token = resp.json()["token"]
            self.token_expires = datetime.datetime.fromisoformat(resp.json()["expires"])
        else:
            post_token_body = {
                "identity": self.username,
                "scope": "user",
                "secret": password
            }
            resp = requests.post(f"{self.base_url}/tokens", json=post_token_body)
            if resp.status_code == 200:
                self.token = resp.json()["token"]
                self.token_expires = datetime.datetime.fromisoformat(resp.json()["expires"])
            elif resp.status_code == 401:
                raise ValueError("Invalid credentials")

    def refresh_token(self) -> None:
        now = datetime.datetime.now(datetime.timezone.utc)

        diff = self.token_expires - now
        diff_in_minutes = diff.total_seconds() / 60

        if diff_in_minutes > 0 and diff_in_minutes <= 10:
            self.__auth(refresh=True)
        elif diff_in_minutes <= 0:
            raise ValueError("Credentials expired")

    def __init__(self, base_url: str, username: str, password: str):
        if "/api" not in base_url:
            base_url = base_url + "/api"
        self.base_url = base_url
        self.username = username
        self.__auth(password=password)
        self.headers = {
            "Authorization": f"Bearer {self.token}"
        }

    def get_certificates(self):
        return requests.get(f"{self.base_url}/nginx/certificates", headers=self.headers).json()
    
    def download_certificate(self, id, target_path):
        response = requests.get(f"{self.base_url}/nginx/certificates/{id}/download", stream=True, headers=self.headers)
        response.raise_for_status()

        with open(target_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
def run():
    api = NginxProxyManagerApi(os.getenv("NGINX_PROXY_MANAGER_URL"), os.getenv("NGINX_PROXY_MANAGER_USERNAME"), os.getenv("NGINX_PROXY_MANAGER_PASSWORD"))
    certificate_list = api.get_certificates()

    cert_id: int
    for certficate_entry in certificate_list:
        if os.getenv("NGINX_PROXY_MANAGER_CERT_NAME") in certficate_entry["nice_name"]:
            cert_id = certficate_entry["id"]
            break

    api.download_certificate(cert_id, f"/tmp/certificates-{datetime.date.today()}.zip")