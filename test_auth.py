import requests
import random
import string

BASE_URL = "http://127.0.0.1:8000/api/auth/"

def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def test_auth():
    username = f"user_{get_random_string(5)}"
    password = "testpassword123"
    email = f"{username}@example.com"

    print(f"--- Probando Registro para {username} ---")
    reg_data = {
        "username": username,
        "password": password,
        "email": email,
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        r_reg = requests.post(f"{BASE_URL}registro/", json=reg_data)
        print(f"Status Registro: {r_reg.status_code}")
        print(f"Respuesta Registro: {r_reg.json()}")
        
        if r_reg.status_code == 201:
            print(f"\n--- Probando Login para {username} ---")
            login_data = {
                "username": username,
                "password": password
            }
            r_login = requests.post(f"{BASE_URL}login/", json=login_data)
            print(f"Status Login: {r_login.status_code}")
            json_login = r_login.json()
            print(f"Respuesta Login: {json_login}")
            
            if "user" in json_login and "access" in json_login:
                print("\n✅ VERIFICACIÓN EXITOSA: Los datos del usuario están en la respuesta y el token fue generado.")
            else:
                print("\n❌ FALLO: No se encontraron datos de usuario o token en la respuesta.")
        else:
            print("\n❌ FALLO: No se pudo crear el usuario.")
            
    except Exception as e:
        print(f"Error durante la prueba: {e}")

if __name__ == "__main__":
    test_auth()
