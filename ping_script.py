import time
import requests

URL = "https://melike1.onrender.com"  # Render'daki Flask uygulamanızın URL'si
PING_INTERVAL = 600  # 600 saniye = 10 dakika


def ping():
    try:
        response = requests.get(URL)
        if response.status_code == 200:
            print("Ping başarılı, uygulama aktif.")
        else:
            print(f"Ping başarısız! Durum: {response.status_code}")
    except requests.RequestException as e:
        print(f"Ping sırasında bir hata oluştu: {e}")


if __name__ == "__main__":
    while True:
        ping()
        time.sleep(PING_INTERVAL)