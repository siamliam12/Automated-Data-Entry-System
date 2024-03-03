import secrets

# Generate a random secret key with 256 bits of entropy
secret_key = secrets.token_urlsafe(32)

print("Random Secret Key:", secret_key)
