import logging


class EncryptionService(object):

    def __init__(self, encryption_class):
        logging.debug('init using {}'.format(encryption_class.__name__))
        self.encryption = encryption_class()
        self.public_key = None

    def generate_key_pair(self, key_length):
        return self.encryption.generate_key_pair(key_length)

    def set_public_key(self, public_key):
        self.public_key = self.encryption.get_deserialized_public_key(public_key)

    def encrypt_collection(self, collection, precision=1e-5):
        return self.encryption.encrypt_collection(self.public_key, collection, precision)

    def decrypt_collection(self, private_key, collection):
        return self.encryption.decrypt_collection(private_key, collection)

    def decrypt_and_deserialize_collection(self, private_key, collection):
        return [self.encryption.decrypt_value(private_key, x)
                for x in self.get_deserialized_collection(collection)]

    def get_serialized_encrypted_collection(self, collection, precision=1e-5):
        return [self.__get_serialized_encrypted_value(x) for x in self.encrypt_collection(collection, precision)]

    def get_serialized_collection(self, collection):
        return [self.__get_serialized_encrypted_value(x) for x in collection]

    def get_deserialized_collection(self, collection):
        return [self.__get_deserialized_encrypted_value(x) for x in collection]

    def __get_serialized_encrypted_value(self, value):
        return self.encryption.get_serialized_encrypted_number(value)

    def __get_deserialized_encrypted_value(self, value):
        return self.encryption.get_encrypted_number(self.public_key, value)
