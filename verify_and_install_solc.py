import solcx

# Verificar versiones de solc disponibles para instalar
print("Versiones disponibles para instalar:")
print(solcx.get_installable_solc_versions())

# Instalar la versión de solc que necesitas
version = '0.8.0'
print(f"Instalando solc {version}...")
solcx.install_solc(version)

# Verificar versiones de solc instaladas
print("Versiones instaladas:")
print(solcx.get_installed_solc_versions())
