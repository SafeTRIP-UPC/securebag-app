
// Importar Web3.js
const Web3 = require('web3');

// Configurar proveedor de Web3 (usando Infura)
const web3 = new Web3(new Web3.providers.HttpProvider('https://ropsten.infura.io/v3/your_infura_project_id'));

// Dirección del contrato y ABI (interfaz del contrato)
const contractAddress = 'your_contract_address'; // Reemplazar con la dirección del contrato
const contractABI = [
    // ABI del contrato inteligente
];

// Crear una instancia del contrato
const contractInstance = new web3.eth.Contract(contractABI, contractAddress);

// Dirección del usuario y su clave privada (para firmar transacciones)
const userAddress = 'your_ethereum_address'; // Reemplazar con tu dirección de Ethereum
const privateKey = 'your_private_key'; // Reemplazar con tu clave privada

// Función para aceptar la cotización en el contrato
async function acceptQuote() {
    try {
        // Obtener la cuenta que firmará la transacción
        const account = web3.eth.accounts.privateKeyToAccount(privateKey);

        // Construir la transacción
        const tx = contractInstance.methods.acceptQuote();

        // Firmar la transacción
        const signedTx = await account.signTransaction({
            to: contractAddress,
            data: tx.encodeABI(),
            gas: await tx.estimateGas(),
        });

        // Enviar la transacción
        const txReceipt = await web3.eth.sendSignedTransaction(signedTx.rawTransaction);
        
        console.log('Transaction hash:', txReceipt.transactionHash);
    } catch (error) {
        console.error('Error:', error);
    }
}

// Llamar a la función para aceptar la cotización
acceptQuote();
