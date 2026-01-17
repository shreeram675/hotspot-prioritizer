import bcrypt

password_to_test = "admin123"
stored_hash = "$2b$12$4JxGPzcJ64YE9iUQy0sRH.XmKL5Ec5IQX859FuFxdkOoR7kLwt2Lq"

password_bytes = password_to_test.encode('utf-8')
hash_bytes = stored_hash.encode('utf-8')

try:
    result = bcrypt.checkpw(password_bytes, hash_bytes)
    print(f"Password verification: {result}")
except Exception as e:
    print(f"Error: {e}")
