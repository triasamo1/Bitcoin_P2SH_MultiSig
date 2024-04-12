from bitcoinutils.setup import setup
from bitcoinutils.keys import PublicKey, P2shAddress
from bitcoinutils.script import Script
import click
import sys

@click.command()
@click.option('--pub_1', default=None, help='Public Key 1 (User 1)')
@click.option('--pub_2', default=None, help='Public Key 2 (User 2)')
@click.option('--pub_3', default=None, help='Public Key 3 (User 3)')

def main(pub_1, pub_2, pub_3):

    if not (pub_1 and pub_2 and pub_3):
        print("[ERROR] Please provide 3 public keys as arguments")
        sys.exit(1)
    
    # Setup network to regtest
    setup('regtest')

    print("\n\n ==========  Public Keys ==========")
    print("\nUser 1: ", pub_1)
    print("\nUser 2: ", pub_2)
    print("\nUser 3: ", pub_3)

    # create the redeem script
    redeem_script = Script(['OP_2', pub_1, pub_2, pub_3, 'OP_3', 'OP_CHECKMULTISIG'])

    # create a P2SH address from a redeem script
    p2sh_address = P2shAddress.from_script(redeem_script)
    print("\nP2SH address: ", p2sh_address.to_string(),"\n")


if __name__ == "__main__":
    main()

# python locking_script.py --pub_1 0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798 --pub_2 02c6047f9441ed7d6d3045406e95c07cd85c778e4b8cef3ca7abac09b95c709ee5 --pub_3 02f9308a019258c31049344f85f89d5229b531c845836f99b08601f113bce036f9