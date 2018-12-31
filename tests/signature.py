from binascii import unhexlify, hexlify, Error

from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_PSS
import uuid


def verify_signature(public_key_string, signature, string):
    try:
        signature_bytes = unhexlify(signature)
    except Error as e:
        print(e)
        return False

    public_key = RSA.importKey(public_key_string)
    hasher = SHA256.new()
    hasher.update(string.encode("utf-8"))

    verifier = PKCS1_PSS.new(public_key)
    return verifier.verify(hasher, signature_bytes)


def create_signature(private_key_string, string):
    private_key = RSA.importKey(private_key_string)
    hasher = SHA256.new()
    hasher.update(string.encode("utf-8"))

    signer = PKCS1_PSS.new(private_key)
    return str(hexlify(signer.sign(hasher)), "utf-8")


def create_security_token(private_key_string, string):
    salt = uuid.uuid4()
    signature = create_signature(private_key_string, salt.hex + ":" + string)
    return salt.hex + signature


def verify_security_token(public_key_string, salted_signature, string):
    salt = salted_signature[:32]
    signature = salted_signature[32:]
    return verify_signature(public_key_string, signature, salt + ":" + string)


if __name__ == "__main__":
    public_key = open("id_rsa.pub").read()
    private_key = open("id_rsa").read()
    token = create_security_token(private_key, "abcde")
    result = verify_security_token(public_key, token, "abcde")
    print(result)
