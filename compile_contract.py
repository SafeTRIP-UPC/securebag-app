import json
from solcx import compile_standard, set_solc_version, install_solc

# Instalar y configurar la versión del compilador Solidity
install_solc('0.8.0')
set_solc_version('0.8.0')

# Leer el archivo SimpleStorage.sol
with open('SimpleStorage.sol', 'r') as file:
    simple_storage_file = file.read()

# Compilar el contrato
compiled_sol = compile_standard({
    "language": "Solidity",
    "sources": {
        "SimpleStorage.sol": {
            "content": simple_storage_file
        }
    },
    "settings": {
        "outputSelection": {
            "*": {
                "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
            }
        }
    }
})

# Guardar la compilación en un archivo JSON
with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file, indent=4)

# Extraer ABI y bytecode
abi = compiled_sol['contracts']['SimpleStorage.sol']['SimpleStorage']['abi']
bytecode = compiled_sol['contracts']['SimpleStorage.sol']['SimpleStorage']['evm']['bytecode']['object']

# Guardar ABI en un archivo
with open("SimpleStorage_abi.json", "w") as file:
    json.dump(abi, file, indent=4)

# Guardar bytecode en un archivo
with open("SimpleStorage_bytecode.txt", "w") as file:
    file.write(bytecode)

print("ABI y Bytecode generados con éxito.")
