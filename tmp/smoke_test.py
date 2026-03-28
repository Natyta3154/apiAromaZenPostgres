import requests

BASE_URL = "http://127.0.0.1:8000/api/"

def run_tests():
    report = []
    
    # 1. Health Check
    try:
        r = requests.get(f"{BASE_URL}health/")
        report.append(f"SMOKE TEST - HEALTH CHECK: {'PASSED' if r.status_code == 200 else 'FAILED'} ({r.status_code})")
    except Exception as e:
        report.append(f"SMOKE TEST - HEALTH CHECK: ERROR ({e})")

    # 2. API Documentation (Swagger/OpenAPI)
    try:
        r_schema = requests.get(f"{BASE_URL}schema/")
        r_docs = requests.get(f"{BASE_URL}docs/")
        report.append(f"SMOKE TEST - SCHEMA (OpenAPI): {'PASSED' if r_schema.status_code == 200 else 'FAILED'} ({r_schema.status_code})")
        report.append(f"SMOKE TEST - SWAGGER UI: {'PASSED' if r_docs.status_code == 200 else 'FAILED'} ({r_docs.status_code})")
    except Exception as e:
        report.append(f"SMOKE TEST - DOCS: ERROR ({e})")

    # 3. Product Catalog
    try:
        r_products = requests.get(f"{BASE_URL}productos/lista/")
        report.append(f"FUNCTIONAL TEST - PRODUCT LIST: {'PASSED' if r_products.status_code == 200 else 'FAILED'} - Found {len(r_products.json())} products.")
    except Exception as e:
        report.append(f"FUNCTIONAL TEST - PRODUCTS: ERROR ({e})")

    # 4. Security (Unauthorized Access to Cart)
    try:
        r_cart = requests.get(f"{BASE_URL}carrito/")
        report.append(f"SECURITY TEST - PROTECTED ROUTE (UNAUTHORIZED): {'PASSED' if r_cart.status_code == 401 else 'FAILED'} - Response: {r_cart.status_code}")
    except Exception as e:
        report.append(f"SECURITY TEST - CART: ERROR ({e})")

    return report

if __name__ == "__main__":
    results = run_tests()
    for res in results:
        print(res)
