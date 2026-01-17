import bcrypt

password_to_test = "admin123"
stored_hash = "$2b$12$IQ4AC03cAeXD/800Sr.h7e9DCKaapMhjfgJdDij7QE7EvFJ8Iqps2"

password_bytes = password_to_test.encode('utf-8')
hash_bytes = stored_hash.encode('utf-8')

try:
    result = bcrypt.checkpw(password_bytes, hash_bytes)
    print(f"Password verification: {result}")
except Exception as e:
    print(f"Error: {e}")
    print(f"Password bytes length: {len(password_bytes)}")
    print(f"Hash bytes length: {len(hash_bytes)}")
    print(f"Hash string: {stored_hash}")
