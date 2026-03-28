import requests
import random
import string

BASE_URL = "http://127.0.0.1:8000/api/"

def get_random_string(length):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

def run_mp_test():
    username = f"tester_{get_random_string(5)}"
    password = "testerpassword123"
    email = f"{username}@example.com"
    
    # 1. Login
    print(f"--- 1. Preparando Usuario ({username}) ---")
    requests.post(f"{BASE_URL}auth/registro/", json={
        "username": username, "password": password, "email": email, "first_name": "QA", "last_name": "Test"
    })
    r_login = requests.post(f"{BASE_URL}auth/login/", json={"username": username, "password": password})
    token = r_login.json().get('access')
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Checkout (Create Preference) using pagos endpoint
    print("--- 2. Creando Preferencia de Pago via /api/pagos/crear-preferencia/ ---")
    payload = {
        "items": [
            {"producto_id": 11, "cantidad": 2}
        ],
        "envio": {
            "direccion": "Calle Falsa 123",
            "ciudad": "CABA",
            "provincia": "Buenos Aires",
            "codigo_postal": "1425"
        }
    }
    r_checkout = requests.post(f"{BASE_URL}pagos/crear-preferencia/", json=payload, headers=headers)
    print(f"Status Checkout: {r_checkout.status_code}")
    checkout_data = r_checkout.json()
    
    if r_checkout.status_code == 200:
        preference_id = checkout_data.get('preference_id')
        orden_id = checkout_data.get('orden_id')
        url_pago = checkout_data.get('url_pago')
        print(f"✅ PREFERENCIA CREADA CORRECTAMENTE!")
        print(f"   ID Preferencia: {preference_id}")
        print(f"   ID Orden: {orden_id}")
        print(f"   URL de Pago (Init Point): {url_pago}")
    else:
        print(f"❌ FALLO AL CREAR PREFERENCIA: {checkout_data}")

if __name__ == "__main__":
    run_mp_test()
