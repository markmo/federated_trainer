class HomomorphicEncryption(object):
    """ Protocol for crypto implementations such as `PheEncryption` """

    def generate_key_pair(self, key_length):
        pass

    def encrypt_collection(self, public_key, collection, precision):
        pass

    def decrypt_collection(self, private_key, collection):
        pass

    def get_deserialized_public_key(self, public_key):
        pass

    def get_encrypted_number(self, public_key, value):
        pass

    def get_serialized_encrypted_number(self, value):
        pass

    def decrypt_value(self, private_key, value):
        pass
