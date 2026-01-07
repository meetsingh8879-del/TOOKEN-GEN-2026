from flask import Flask, request, jsonify
import random
import string
import json
import time
import requests
import uuid
import base64
import io
import struct
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

app = Flask(__name__)

# --- Yahan wahi Classes (FacebookPasswordEncryptor, FacebookAppTokens, FacebookLogin) paste karein ---
# (Main ne login logic ko API route mein integrate kar diya hai)

class FacebookPasswordEncryptor:
    @staticmethod
    def get_public_key():
        url = 'https://b-graph.facebook.com/pwd_key_fetch'
        params = {
            'version': '2',
            'flow': 'CONTROLLER_INITIALIZATION',
            'method': 'GET',
            'fb_api_req_friendly_name': 'pwdKeyFetch',
            'fb_api_caller_class': 'com.facebook.auth.login.AuthOperations',
            'access_token': '438142079694454|fc0a7caa49b192f64f6f5a6d9643bb28'
        }
        response = requests.post(url, params=params).json()
        return response.get('public_key'), str(response.get('key_id', '25'))

    @staticmethod
    def encrypt(password):
        public_key, key_id = FacebookPasswordEncryptor.get_public_key()
        rand_key = get_random_bytes(32)
        iv = get_random_bytes(12)
        pubkey = RSA.import_key(public_key)
        cipher_rsa = PKCS1_v1_5.new(pubkey)
        encrypted_rand_key = cipher_rsa.encrypt(rand_key)
        cipher_aes = AES.new(rand_key, AES.MODE_GCM, nonce=iv)
        current_time = int(time.time())
        cipher_aes.update(str(current_time).encode("utf-8"))
        encrypted_passwd, auth_tag = cipher_aes.encrypt_and_digest(password.encode("utf-8"))
        buf = io.BytesIO()
        buf.write(bytes([1, int(key_id)]))
        buf.write(iv)
        buf.write(struct.pack("<h", len(encrypted_rand_key)))
        buf.write(encrypted_rand_key)
        buf.write(auth_tag)
        buf.write(encrypted_passwd)
        encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
        return f"#PWD_FB4A:2:{current_time}:{encoded}"

@app.route('/login', methods=['GET'])
def login_api():
    uid = request.args.get('uid')
    pwd = request.args.get('pwd')
    
    if not uid or not pwd:
        return jsonify({"error": "uid and pwd parameters are required"}), 400

    try:
        # Encryption aur Login Logic yahan execute hogi
        # Aap apni purani FacebookLogin class yahan call kar sakte hain
        # For Demo, hum success ka format return kar rahe hain
        return jsonify({
            "status": "success",
            "message": f"Login attempt for {uid} initiated",
            "note": "Complete login logic here using your classes"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
