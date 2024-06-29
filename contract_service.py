import json
from flask import Flask, request, jsonify
from web3 import Web3
from solcx import compile_standard, install_solc, set_solc_version

app = Flask(__name__)

# Web3 setup
infura_url = "https://sepolia.infura.io/v3/8dfbd60140824e0fb77182ea00aae180"
web3 = Web3(Web3.HTTPProvider(infura_url))

account_address = "0xA6AA71b0A39FcDBDd990f4c20644337E6CdFe383"
private_key = "9b48cbe54593ce2a226c2be52151335c8ac9b2c32adfb475b2e28a11a8723220"

@app.route('/deploy_contract', methods=['POST'])
def generate_contract():
    data = request.json
    estimated_value = int(data['value'])

    # Obtener el nonce
    nonce = web3.eth.get_transaction_count(account_address, 'pending')
    print(f"Nonce obtenido: {nonce}")

    # Verificar el balance
    balance = web3.eth.get_balance(account_address)
    print(f"Balance: {balance} wei")

    # Leer ABI y Bytecode desde los archivos
    with open('SimpleStorage_abi.json', 'r') as file:
        abi = json.load(file)

    with open('SimpleStorage_bytecode.txt', 'r') as file:
        bytecode = file.read()

    # Crear contrato
    SimpleStorage = web3.eth.contract(abi=abi, bytecode=bytecode)

    # Ajustar gas y gasPrice para la transacción
    gas_limit = 150000  # Límite de gas ajustado
    gas_price = web3.to_wei('30', 'gwei')  # Precio de gas ajustado

    # Construir transacción de despliegue
    construct_txn = SimpleStorage.constructor().build_transaction({
        'from': account_address,
        'nonce': nonce,
        'gas': gas_limit,
        'gasPrice': gas_price
    })
    print(f"Transacción de despliegue construida: {construct_txn}")

    # Firmar y enviar la transacción
    signed_txn = web3.eth.account.sign_transaction(construct_txn, private_key)
    txn_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print(f"Hash de la transacción enviada: {txn_hash.hex()}")

    # Esperar el recibo de la transacción
    try:
        txn_receipt = web3.eth.wait_for_transaction_receipt(txn_hash, timeout=300)
        print(f"Recibo de la transacción: {txn_receipt}")

        # Interactuar con el contrato desplegado
        contract_instance = web3.eth.contract(address=txn_receipt.contractAddress, abi=abi)
        payment_transaction = contract_instance.functions.setValue(estimated_value).build_transaction({
            'chainId': web3.eth.chain_id,
            'from': account_address,
            'nonce': nonce + 1,
            'gas': gas_limit,
            'gasPrice': gas_price
        })

        # Firmar y enviar la transacción de pago
        signed_payment_txn = web3.eth.account.sign_transaction(payment_transaction, private_key)
        payment_txn_hash = web3.eth.send_raw_transaction(signed_payment_txn.rawTransaction)
        print(f"Hash de la transacción de pago enviada: {payment_txn_hash.hex()}")

        # Esperar el recibo de la transacción de pago
        payment_txn_receipt = web3.eth.wait_for_transaction_receipt(payment_txn_hash, timeout=300)
        print(f"Recibo de la transacción de pago: {payment_txn_receipt}")

        # Convertir AttributeDict a dict para serializar
        txn_receipt_dict = {k: (v.hex() if isinstance(v, bytes) else v) for k, v in dict(txn_receipt).items()}
        payment_txn_receipt_dict = {k: (v.hex() if isinstance(v, bytes) else v) for k, v in dict(payment_txn_receipt).items()}

        return jsonify({
            'message': 'Contrato inteligente generado con éxito',
            'txn_receipt': txn_receipt_dict,
            'payment_txn_receipt': payment_txn_receipt_dict
        })
    except Exception as e:
        print(f"Error esperando el recibo de la transacción: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5003)
