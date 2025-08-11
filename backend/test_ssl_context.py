import ssl
import os

CA_CERT_PATH = "d:\\Projects\\Klymate-AI\\backend\\app\\core\\tidb-ca.pem"
print(f"Using CA certificate path: {CA_CERT_PATH}")
print(f"Certificate exists: {os.path.exists(CA_CERT_PATH)}")

try:
    ssl_context = ssl.create_default_context(cafile=CA_CERT_PATH)
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    print("SSL context created successfully.")
except ssl.SSLError as e:
    print(f"SSL error: {e}")
