from phe_encryption import PheEncryption


conf = {
    'n_segments': 5,
    'federated_trainer_host': 'http://localhost:8080',
    'eta': 1.5,
    'registration_enabled': True,
    'encryption': PheEncryption,
    'encryption_active': True,
    'precision': 1e-5,
}
