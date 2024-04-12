# Bitcoin | P2SH -> P2PKH (2-3 MULTISIG)

Library used: **bitcoin-utils**

__________________________
The **locking_script.py** creates a P2SH Bitcoin address that implements a MULTISIG scheme,
where all funds sent to it should be locked until 2 out of 3 potential signers sign a transaction
to move the funds elsewhere.
This script :
- accepts 3 public keys for the purpose of creating the P2SH address that will
implement a 2-of-3 MULTISIG scheme
- displays the P2SH address

__________________________
The **unlocking_script.py** will allow spending all funds from this P2SH address.
This script:
- accepst 2 private keys (used to sign transactions) and 1 public key (to recreate the
redeem script as above – the other two public keys may be derived from the provided
private keys)
- accepts a P2SH address to get the funds from (the one created by the first script)
- accepts a P2PKH address to send the funds to
- checks if the P2SH address has any UTXOs to get funds from
- calculates the appropriate fees with respect to the size of the transaction
- sends all funds that the P2SH address received to the P2PKH address provided
- displays the raw unsigned transaction
- signs the transaction
- displays the raw signed transaction
- displays the transaction id
- verifies that the transaction is valid and will be accepted by the Bitcoin nodes
- if the transaction is valid, it sends it to the blockchain
