import requests

BASE_URL = "http://127.0.0.1:8000/api/"

def run_tests():
    report = []
    
    # 1. Login with invalid credentials
    r_bad_login = requests.post(f"{BASE_URL}auth/login/", json={"username": "non_existent_user", "password": "wrong_password"})
    report.append(f"AUTHENTICATION - INVALID CREDENTIALS: {'PASSED' if r_bad_login.status_code == 401 else 'FAILED'} (Got {r_bad_login.status_code})")
    
    # 2. Get non-existent product
    r_bad_product = requests.get(f"{BASE_URL}productos/999999/") # Assuming this ID doesn't exist
    report.append(f"PRODUCT MANAGER - NON-EXISTENT PRODUCT: {'PASSED' if r_bad_product.status_code == 404 else 'FAILED'} (Got {r_bad_product.status_code})")
    
    # 3. Access cart as guest
    r_guest_cart = requests.get(f"{BASE_URL}carrito/")
    report.append(f"CART MANAGER - UNAUTHORIZED ACCESS: {'PASSED' if r_guest_cart.status_code == 401 else 'FAILED'} (Got {r_guest_cart.status_code})")
    
    # 4. Accessing Redoc
    r_redoc = requests.get(f"{BASE_URL}redoc/")
    report.append(f"DOCUMENTATION - REDOC UI: {'PASSED' if r_redoc.status_code == 200 else 'FAILED'} (Got {r_redoc.status_code})")
    
    # 5. Accessing Schema JSON
    r_schema = requests.get(f"{BASE_URL}schema/")
    report.append(f"DOCUMENTATION - SCHEMA JSON: {'PASSED' if r_schema.status_code == 200 else 'FAILED'} (Got {r_schema.status_code})")

    return report

if __name__ == "__main__":
    results = run_tests()
    for res in results:
        print(res)
