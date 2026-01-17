import bcrypt

password_to_test = "admin123"
stored_hash = "$2b$12$BBulZg19vjAOAL3oCHZW6unWakb4ysDGNj0Bm/OqlaVVJNB9c2rve"

password_bytes = password_to_test.encode('utf-8')
hash_bytes = stored_hash.encode('utf-8')

result = bcrypt.checkpw(password_bytes, hash_bytes)
print(f"Password verification: {result}")
