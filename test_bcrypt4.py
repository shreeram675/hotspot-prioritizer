import bcrypt

password_to_test = "admin123"
stored_hash = "$2b$12$wdSlivtVPUS.sBH.WEl5UO5EJ8aDV18XC0gvOHQ.7nlEKq1fL5Z1y"

password_bytes = password_to_test.encode('utf-8')
hash_bytes = stored_hash.encode('utf-8')

result = bcrypt.checkpw(password_bytes, hash_bytes)
print(f"Password verification: {result}")
