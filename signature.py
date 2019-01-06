import nacl.signing
import nacl.encoding

from binascii import unhexlify, hexlify, Error

import uuid
import os.path
import sys

import configargparse


def create_signature(key, item):
    signing_key = nacl.signing.SigningKey(key, encoder=nacl.encoding.HexEncoder)
    signed = signing_key.sign(item)
    return signed


def verify_signature(key, signature):
    signing_key = nacl.signing.SigningKey(key, encoder=nacl.encoding.HexEncoder)
    verify_key = signing_key.verify_key
    signed = nacl.signing.SignedMessage(signature)
    return verify_key.verify(signed)


def generate():
    signing_key = nacl.signing.SigningKey.generate()
    return signing_key.encode(encoder=nacl.encoding.HexEncoder).decode("ascii")


def setup_parser():
    parser = configargparse.ArgumentParser(description="PyNaCl signing module")
    subparsers = parser.add_subparsers(
        title="command", dest="command", help="subcommand help"
    )
    parser_generate = subparsers.add_parser("generate", help="generate a new key")
    parser_sign = subparsers.add_parser("sign", help="sign a string")
    parser_verify = subparsers.add_parser("verify", help="verify a signed string")

    parser_sign.add_argument("--key", type=lambda s: s.encode("ascii"), required=True)
    parser_sign.add_argument("--data", type=lambda s: s.encode("utf-8"), required=True)

    parser_verify.add_argument("--key", type=lambda s: s.encode("ascii"), required=True)
    parser_verify.add_argument("--signature", type=bytes.fromhex, required=True)

    return parser


if __name__ == "__main__":
    parser = setup_parser()
    args = parser.parse_args()
    if args.command == "generate":
        print(generate())
    elif args.command == "sign":
        print(create_signature(args.key, args.data).hex())
    elif args.command == "verify":
        print(verify_signature(args.key, args.signature).decode("utf-8"))
    sys.exit(0)

    if not os.path.isfile("signing_key"):
        signing_key = nacl.signing.SigningKey.generate()
        with open("signing_key", "w") as key_file:
            key_file.write(
                signing_key.encode(encoder=nacl.encoding.HexEncoder).decode("ascii")
            )
    else:
        with open("signing_key", "r") as key_file:
            signing_key_hex = key_file.read().encode("ascii")
            signing_key = nacl.signing.SigningKey(
                signing_key_hex, encoder=nacl.encoding.HexEncoder
            )

    signed = signing_key.sign(b"Attack at dawn")
    signed_message_hex = signed.hex()
    bytes_2 = bytes.fromhex(signed_message_hex)
    signed_2 = nacl.signing.SignedMessage(bytes_2)
    print("-----")
    print(signed_message_hex)
    print("=====")
    print(signed_2.hex())
    print("----")

    verify_key = signing_key.verify_key
    print(verify_key.verify(signed_2))
    print("+++++++++++++++++++++")
    signing_key_hex = signing_key.encode(encoder=nacl.encoding.HexEncoder)
    signature = create_signature(signing_key_hex, b"Attack at dawn")
    print(signature)
    print(verify_signature(signing_key_hex, signature))
