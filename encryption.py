from cryptography.fernet import Fernet


def generate_key():
    return Fernet.generate_key()


def encrypt_data(data, key):
    fernet = Fernet(key)
    return fernet.encrypt(data.encode('utf-8'))


def decrypt_data(encrypted_data, key):
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_data).decode('utf-8')
