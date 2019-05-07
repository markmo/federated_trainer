from phe_encryption import PheEncryption


conf = {
    'server_registration_url': 'http://localhost:8080/models',
    'port': 9090,
    'encryption': PheEncryption,
    'key_length': 4096,  # necessary to avoid overflow (vs. default 1024), but really slow
    'encryption_active': True,
}
