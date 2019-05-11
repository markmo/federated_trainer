import phe as paillier

from homomorphic_encryption import HomomorphicEncryption


class PheEncryption(HomomorphicEncryption):
    """
    Implements partially homomorphic encryption.

    The homomorphic properties of the Paillier crypto system are:
    * Encrypted numbers can be multiplied by a non encryption_active scalar
    * Encrypted numbers can be added together
    * Encrypted numbers can be added to non encryption_active scalars
    """

    def generate_key_pair(self, key_length):
        return paillier.generate_paillier_keypair(n_length=key_length)

    def encrypt_collection(self, public_key, collection, precision=1e-5):
        if any([type(x) == paillier.EncryptedNumber for x in collection]):
            return collection
        else:
            return [public_key.encrypt(x, precision) for x in collection]

    def decrypt_collection(self, private_key, collection):
        return [private_key.decrypt(x) for x in collection]

    def get_deserialized_public_key(self, public_key):
        return paillier.PaillierPublicKey(n=int(public_key))

    def get_encrypted_number(self, public_key, value):
        ciphertext, exponent = value['ciphertext'], value['exponent']
        return paillier.EncryptedNumber(public_key, int(ciphertext), int(exponent))

    def get_serialized_encrypted_number(self, value):
        return dict(ciphertext=str(value.ciphertext()), exponent=value.exponent)

    def decrypt_value(self, private_key, value):
        return private_key.decrypt(value)
