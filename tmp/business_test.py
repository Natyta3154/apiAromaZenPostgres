import requests

BASE_URL = "http://127.0.0.1:8000/api/"

def run_business_tests():
    report = []
    
    # 1. Product Stock Validation
    # We saw product 11 has stock 20 (from previous run)
    print("--- Testing Stock Validation ---")
    # Need to login first to use cart
    requests.post(f"{BASE_URL}auth/registro/", json={"username": "stock_tester", "password": "password", "email": "stock@test.com"})
    r_login = requests.post(f"{BASE_URL}auth/login/", json={"username": "stock_tester", "password": "password"})
    token = r_login.json().get('access')
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to add 1000 units (more than 20)
    r_bad_stock = requests.post(f"{BASE_URL}carrito/agregar/", json={"producto_id": 11, "cantidad": 1000}, headers=headers)
    report.append(f"BUSINESS - STOCK REJECTION (Overlimit): {'PASSED' if r_bad_stock.status_code == 400 else 'FAILED'} (Got {r_bad_stock.status_code})")
    
    # 2. Duplicate User Registration
    print("--- Testing Duplicate Registration ---")
    r_duplicate = requests.post(f"{BASE_URL}auth/registro/", json={"username": "stock_tester", "password": "password", "email": "other@test.com"})
    report.append(f"BUSINESS - DUPLICATE USER REGISTRATION: {'PASSED' if r_duplicate.status_code == 400 else 'FAILED'} (Got {r_duplicate.status_code})")
    
    # 3. Blog Retrieval
    print("--- Testing Blog Feed ---")
    r_blog = requests.get(f"{BASE_URL}blog/posts/")
    report.append(f"BUSINESS - BLOG RETRIEVAL: {'PASSED' if r_blog.status_code == 200 else 'FAILED'} (Found {len(r_blog.json()) if isinstance(r_blog.json(), list) else 'N/A'} posts)")

    return report

if __name__ == "__main__":
    results = run_business_tests()
    for res in results:
        print(res)
