from bitcoinutils.setup import setup
from bitcoinutils.keys import PublicKey, PrivateKey, P2shAddress, P2pkhAddress
from bitcoinutils.script import Script
import click
import sys
from bitcoinutils.proxy import NodeProxy
import requests
from bitcoinutils.utils import to_satoshis
from bitcoinutils.transactions import TxInput, Transaction, TxOutput

@click.command()
@click.option('--priv_1', default=None, help='Private Key (any of the 3))')
@click.option('--priv_2', default=None, help='Private Key (any of the 3)')
@click.option('--pub_3', default=None, help='Public Key 3 (the remaining one)')
@click.option('--source_addr', default=None, help='The P2SH address that was created by the locking script')
@click.option('--target_addr', default=None, help='The PS2PKH address to send BTC to')
@click.option('--rpcuser', default=None, help='The rpcuser that is maintained in your bitcoin.conf')
@click.option('--rpcpassword', default=None, help='The rpcpassword that is maintained in your bitcoin.conf')

def main(priv_1, priv_2, pub_3, source_addr, target_addr, rpcuser, rpcpassword):

    if not (priv_1 and priv_2 ):
        print("[ERROR] Please provide the two needed private keys")
        sys.exit(1)

    if not (pub_3):
        print("[ERROR] Please provide the remaining public key")
        sys.exit(1)

    if not (source_addr and target_addr):
        print("[ERROR] Please provide a Source(P2SH) and a Target(P2PKH) address")
        sys.exit(1)
    
    # Setup network to regtest
    setup('regtest')

    # Extract the public keys from the private keys
    priv_1_obj = PrivateKey(priv_1)
    priv_2_obj = PrivateKey(priv_2)
    pub_1 = priv_1_obj.get_public_key()
    pub_2 = priv_2_obj.get_public_key()

    print("\n\n ==========  Public Keys ==========")
    print("\nUser 1: ", pub_1.to_hex(compressed=True))
    print("\nUser 2: ", pub_2.to_hex(compressed=True))
    print("\nUser 3: ", pub_3)

    # Source and target
    p2sh_address = source_addr
    p2pkh_address = P2pkhAddress(target_addr)
    print("\nP2SH Address: ", p2sh_address)
    print("\nP2PKH Address: ", p2pkh_address.to_string())

    proxy = NodeProxy(rpcuser, rpcpassword).get_proxy()
    # count = proxy.getblockcount()
    # print(count)

    # import the p2sh address to 
    proxy.importaddress(p2sh_address)
    # list the unspent utxos
    unspent = proxy.listunspent(1, 9999999, [p2sh_address])

    total_amount = 0
    inputs_list = []
    total_outputs = 0
    #create the inputs of all UTXOs
    for utxo in unspent:
        total_amount = total_amount + to_satoshis(utxo['amount'])
        inputs_list.append(TxInput(utxo['txid'], utxo['vout']))
        total_outputs += int(utxo['vout'])

    
    print("\nUnspent UTXOs: ")
    print(unspent)
    print("\nUnspent Amount available (satoshis): ", total_amount)
    
    if total_amount == 0:
        print("No available funds to spend")
        sys.exit(0)

    # calculate fees based on the transaction size
    transaction_size = len(inputs_list)*180 + total_outputs*34 + 10 + len(inputs_list)
    print("\nTransaction Size (bytes): ", transaction_size)

    # fee_rate = 37920 # satoshis per byte from https://btc.network/estimate
    # fees = fee_rate*transaction_size
    # print("\nTransaction fees (satoshis): ", fees)

    url = 'https://api.blockcypher.com/v1/btc/test3'
    response = requests.get(url)
    fee_per_kb = response.json()['medium_fee_per_kb']
    fees = to_satoshis(transaction_size * fee_per_kb / (1024 * 10 ** 8))
    print("\nTransaction fees (satoshis): ", fees)

    # create transaction output
    amount_after_fees = total_amount - fees
    txout = TxOutput(amount_after_fees, p2pkh_address.to_script_pub_key())
    
    # build transaction object
    tx = Transaction(inputs_list, [txout])
    print("\nRaw unsigned transaction:\n" + tx.serialize())

    # create the redeem script
    redeem_script = Script(['OP_2', pub_1.to_hex(), pub_2.to_hex(), pub_3, 'OP_3', 'OP_CHECKMULTISIG'])
    # Each transaction input has to be signed separately
    for index, txin in enumerate(inputs_list):
        sig_1 = priv_1_obj.sign_input(tx, index, redeem_script)
        sig_2 = priv_2_obj.sign_input(tx, index, redeem_script)
        # CHECKMULTISIG bug
        txin.script_sig = Script(["OP_0", sig_1, sig_2, redeem_script.to_hex()])
        # txin.script_sig = Script([sig_1, sig_2, redeem_script.to_hex()])

    signed_tx = tx.serialize()
    print("\nSigned transaction:\n" + signed_tx)

    tx_id = tx.get_txid()
    print("\nTransaction ID :\n" + tx_id)
    
    # Check if transaction was valid
    tx_result = proxy.testmempoolaccept([signed_tx])
    print(tx_result)

    if tx_result[0]['allowed']:
        print("\nValid Transaction!")
        proxy.sendrawtransaction(signed_tx)
        print("\nTransaction sent to the blockchain!")
    else:
        print("Invalid Transaction!")
        sys.exit(1)
    


if __name__ == "__main__":
    main()

# User 1:  0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
# User 2:  02c6047f9441ed7d6d3045406e95c07cd85c778e4b8cef3ca7abac09b95c709ee5
# User 3:  02f9308a019258c31049344f85f89d5229b531c845836f99b08601f113bce036f9
# P2SH Address:  2MuFU6ZyBLtDNadMA6RnwJdXGWUSUaoKLeS
# P2PKH Address:  n1dDgKfr6gqMCBj7UGHJ3kCnJoBX9djsXx

# python assignment_1/unlocking_script.py --priv_1 cMahea7zqjxrtgAbB7LSGbcQUr1uX1ojuat9jZodMN87JcbXMTcA --priv_2 cMahea7zqjxrtgAbB7LSGbcQUr1uX1ojuat9jZodMN87K7XCyj5v --pub_3 02f9308a019258c31049344f85f89d5229b531c845836f99b08601f113bce036f9  --source_addr 2MuFU6ZyBLtDNadMA6RnwJdXGWUSUaoKLeS --target_addr n1dDgKfr6gqMCBj7UGHJ3kCnJoBX9djsXx