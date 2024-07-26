from bitcoinrpc.authproxy import AuthServiceProxy ,JSONRPCException
from decimal import Decimal, InvalidOperation

rpc_user = 'jowan'
rpc_password = '123456789'
rpc_port = 18443  # Default port for regtest
def create_legacy_wallet(wallet_name):

    wallet_name = wallet_name

    # Connect to the Bitcoin Core RPC server
    rpc_connection = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@127.0.0.1:{rpc_port}")

    # Create wallet with options
    try:
        # The wallet creation RPC command with options
        rpc_connection.createwallet(wallet_name, False, False, "", False, False)
    except Exception as e:
        print(f"Error creating wallet: {e}")
        return None, None

    # Connect to the specific wallet
    wallet_rpc_connection = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@127.0.0.1:{rpc_port}/wallet/{wallet_name}")

    # Generate a new legacy address
    address = wallet_rpc_connection.getnewaddress("", "legacy")

    # Dump private key
    private_key = wallet_rpc_connection.dumpprivkey(address)

    return address, private_key

def send_btc(sender_wallet_name,sender_private_key, recipients, fee_rate_satoshi_per_byte=100):

    wallet_name = sender_wallet_name

    # Connect to the Bitcoin Core RPC server with the specific wallet
    url = f"http://{rpc_user}:{rpc_password}@127.0.0.1:{rpc_port}/wallet/{wallet_name}"
    rpc_connection = AuthServiceProxy(url)

    try:
        # Fetch UTXOs
        utxos = rpc_connection.listunspent()
        inputs = []
        total_input = Decimal('0.0')

        for utxo in utxos:
            if total_input >= sum(recipients.values()):
                break
            inputs.append({
                "txid": utxo['txid'],
                "vout": utxo['vout']
            })
            total_input += Decimal(utxo['amount'])

        if total_input < sum(recipients.values()):
            print("Insufficient funds")
            return None

        # Create the raw transaction with inputs and outputs
        raw_tx = rpc_connection.createrawtransaction(inputs, recipients)

        # Estimate the size of the transaction
        tx_size = len(raw_tx) // 2  # Approximate size in bytes (hex length divided by 2)

        # Calculate the fee based on the fee rate
        fee = Decimal(fee_rate_satoshi_per_byte) * Decimal(tx_size)
        fee_in_btc = fee / Decimal(1e8)  # Convert fee to BTC

        # Ensure there is enough to cover the fee
        total_amount = sum(recipients.values())
        if total_input < total_amount + fee_in_btc:
            print("Insufficient funds to cover the fee")
            return None

        # Add a change address if necessary
        change_address = rpc_connection.getnewaddress()
        outputs_with_change = {**recipients, change_address: total_input - total_amount - fee_in_btc}

        # Create the raw transaction with updated outputs
        raw_tx_with_change = rpc_connection.createrawtransaction(inputs, outputs_with_change)

        # Sign the transaction
        signed_tx = rpc_connection.signrawtransactionwithkey(raw_tx_with_change, [sender_private_key])

        # Check signed transaction details
        if not signed_tx.get('complete', False):
            print(f"Failed to sign transaction: {signed_tx}")
            return None

        # Send the transaction
        tx_id = rpc_connection.sendrawtransaction(signed_tx['hex'])
        print(f"Transaction ID: {tx_id}")
        return tx_id

    except (JSONRPCException, InvalidOperation) as e:
        print(f"Error sending transaction: {e}")
        return None









def get_wallet_balances(wallet_name):
    urlwithoutwallet = f"http://{rpc_user}:{rpc_password}@127.0.0.1:{rpc_port}/"
    rpc_connection_no_wallet = AuthServiceProxy(urlwithoutwallet)
    wallet_name = wallet_name
    try:
        loaded_wallets = rpc_connection.listwallets()
        if wallet_name not in loaded_wallets:
            rpc_connection_no_wallet.loadwallet(wallet_name)
    except Exception as e:
        print(f"Error loading wallet: {e}")

    url = f"http://{rpc_user}:{rpc_password}@127.0.0.1:{rpc_port}/wallet/{wallet_name}"
    rpc_connection = AuthServiceProxy(url)

    try:
        # Get wallet info
        wallet_info = rpc_connection.getwalletinfo()
        balance = wallet_info.get('balance', 0.0)
        unconfirmed_balance = wallet_info.get('unconfirmed_balance', 0.0)
        immature_balance = wallet_info.get('immature_balance', 0.0)

        return {
            'available_balance': balance,
            'pending_balance': unconfirmed_balance,
            'immature_balance': immature_balance
        }
    except JSONRPCException as e:
        print(f"Error retrieving wallet info: {e}")
        return None