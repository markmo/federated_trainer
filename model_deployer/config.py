from phe_encryption import PheEncryption


conf = {
    'server_registration_url': 'http://localhost:8080/models',
    'port': 9090,
    'encryption': PheEncryption,
    'key_length': 1024,
    'encryption_active': True,
}
