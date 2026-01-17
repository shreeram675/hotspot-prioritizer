import bcrypt

password_to_test = "admin123"
stored_hash = "$2b$12$lauaT7bAD5f00hi8Yiz6xu.CKrYeM3mx7XaP26qcqyk6I0YgXa4wu"

password_bytes = password_to_test.encode('utf-8')
hash_bytes = stored_hash.encode('utf-8')

result = bcrypt.checkpw(password_bytes, hash_bytes)
print(f"admin@example.com hash works: {result}")
