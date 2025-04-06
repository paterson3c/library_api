import requests
import json
import uuid
from hashlib import sha1
import logging

"""
client.py
Este script de pruebas automatiza la interacción con el servidor de usuarios y archivos.
Limpia archivos previos, crea usuarios, actualiza contraseñas, realiza inicios de sesión y prueba operaciones con archivos.
"""

SECRET_UUID = uuid.UUID('00010203-0405-0607-0809-0a0b0c0d0e0f')
URL_USER = "http://localhost:5050/"
URL_FILE = "http://localhost:5051/"

def create_token(uid, secret):
     token_hash = uuid.uuid5(secret, uid)
     return f"{token_hash}"

# Inicia la prueba de user.py
print()
print(" >>> EMPIEZA EL TEST DE user.py <<< ")

# Test 1: Creación de usuario "antonio" con contraseña 1234
print()
print("Creando usuario antonio con password 1234...")
print("Debe devolver OK, si ya existe debe devolver ERROR")
print()

url = URL_USER + "create_user/antonio"
headers = {"Content-Type": "application/json"}
data = {"password": "1234"}
reponse = requests.post(url, headers=headers, data=json.dumps(data))

if reponse.status_code == 200:
    print(" >>> [OK]: " + f"{reponse.json()} <<< ")
else:
    print(">>> user antonio ya creado, el test continua pese a devolver [ERROR]: " + f"{reponse.json()} <<< ")

# Test 2: Intento de creación de otro usuario "antonio" con contraseña diferente
print()
print("Creando de nuevo otro usuario antonio con password 12345...")
print("Debe devolver ERROR")
print()

url = URL_USER + "create_user/antonio"
headers = {"Content-Type": "application/json"}
data = {"password": "12345"}
reponse = requests.post(url, headers=headers, data=json.dumps(data))

if reponse.status_code != 200:
    print(">>> ERROR: " + f"{reponse.json()} <<< ")
else:
    raise Exception(" >>> El test 2 debía devolver ERROR y devolvio [OK]: " + f"{reponse.json()} <<< ")

# Test 3: Iniciar sesión con usuario "antonio" usando una contraseña incorrecta (12345)
print()
print("Iniciando sesion de usuario antonio con password 12345...")
print("Debe devolver ERROR y no devolver su uid")
print()

url = URL_USER + "get_user_uid/antonio"
headers = {"Content-Type": "application/json"}
data = {"password": "12345"}
reponse = requests.post(url, headers=headers, data=json.dumps(data))

if reponse.status_code != 200:
    print(" >>> [ERROR]: " + f"{reponse.json()}")
else:
    raise Exception(" >>> El test 3 debia devolver ERROR y devolvio [OK]: " + f"{reponse.json()} <<< ")

# Test 4: Iniciar sesión con usuario "antonio" y la contraseña correcta (1234)
print()
print("Iniciando sesion de usuario antonio con password 1234...")
print("Debe devolver OK y la uid y el token del usuario")
print()

url = URL_USER + "get_user_uid/antonio"
headers = {"Content-Type": "application/json"}
data = {"password": "1234"}
reponse = requests.post(url, headers=headers, data=json.dumps(data))

if reponse.status_code == 200:
    print(" >>> [OK]: " + f"{reponse.json()}")
    UID = reponse.json()["uid"]
    token = uuid.uuid5(SECRET_UUID, UID)
else:
    raise Exception(" >>> El test 4 debia devolver OK y devolvio [ERROR]: " + f"{reponse.json()} <<< ")

# Test 5: Actualizar la contraseña del usuario "antonio" a 123456
print()
print("Actualizando password del usuario antonio a 123456...")
print("Debe devolver OK")
print()

url = URL_USER + "update_password"
headers = {"Content-Type": "application/json"}
headers["Authorization"] = "Bearer " + f"{token}"
data = {"uid": UID, "password": "123456"}
reponse = requests.put(url, headers=headers, data=json.dumps(data))

if reponse.status_code == 200:
    print(" >>> [OK]: " + f"{reponse.json()}")
else:
    raise Exception(" >>> El test 5 debia devolver OK y devolvio [ERROR]: " + f"{reponse.json()} <<< ")

# Test 6: Iniciar sesión con usuario "antonio" y la nueva contraseña (123456)
print()
print("Iniciando sesion de usuario antonio con password 123456...")
print("Debe devolver OK y la uid y el token del usuario")
print()

url = URL_USER + "get_user_uid/antonio"
headers = {"Content-Type": "application/json"}
data = {"password": "123456"}
reponse = requests.post(url, headers=headers, data=json.dumps(data))

if reponse.status_code == 200:
    print(" >>> [OK]: " + f"{reponse.json()}")
else:
    raise Exception(" >>> El test 6 debia devolver OK y devolvio [ERROR]: " + f"{reponse.json()} <<< ")

# Test 7: Eliminar el usuario "antonio"
print()
print("Eliminando usuario antonio...")
print("Debe devolver OK")
print()

url = URL_USER + "delete_user"
headers = {"Content-Type": "application/json"}
headers["Authorization"] = "Bearer " + f"{token}"
data = {"uid": UID}
reponse = requests.post(url, headers=headers, data=json.dumps(data))

if reponse.status_code == 200:
    print(" >>> [OK]: " + f"{reponse.json()}")
else:
    raise Exception(" >>> El test 7 debia devolver OK y devolvio [ERROR]: " + f"{reponse.json()} <<< ")

# Test 8: Crear de nuevo el usuario "antonio" después de haberlo eliminado
print()
print("Creando usuario antonio con password 1234...")
print("Debe devolver OK porque antes fue eliminado")
print()

url = URL_USER + "create_user/antonio"
headers = {"Content-Type": "application/json"}
data = {"password": "1234"}
reponse = requests.post(url, headers=headers, data=json.dumps(data))

if reponse.status_code == 200:
    print(" >>> [OK]: " + f"{reponse.json()} <<< ")
else:
    raise Exception(">>> La creacion de antonio debia ser OK y devolvio [ERROR]: " + f"{reponse.json()} <<< ")

# Test de inicio de sesión para verificar que el usuario fue recreado correctamente
url = URL_USER + "get_user_uid/antonio"
headers = {"Content-Type": "application/json"}
data = {"password": "1234"}
reponse = requests.post(url, headers=headers, data=json.dumps(data))

if reponse.status_code == 200:
    print(" >>> [OK]: " + f"{reponse.json()}")
    UID = reponse.json()["uid"]
    token = create_token(UID, SECRET_UUID)
else:
    raise Exception(" >>> El inicio de sesion de antonio debia ser OK y devolvio [ERROR]: " + f"{reponse.json()} <<< ")

# Finaliza el test de user.py
print()
print(" >>> TERMINA EL TEST DE user.py <<< ")
print()

# Inicio del test de file.py
print()
print()
print(" >>> EMPIEZA EL TEST DE file.py <<< ")

# Test 1: Crear archivo 'fichero_001.txt' con un UID incorrecto ('89')
# Debe devolver un error ya que el UID no pertenece a un usuario válido.
print()
print("Creando archivo fichero_001.txt con el contenido 'texto de prueba del fichero' del usuario con UID '89'...")
print("Debe devolver ERROR")
print()

url = URL_FILE + "create_file/fichero_001.txt"
headers = {}
headers["Content-Type"] = "application/json"
headers["Authorization"] = "Bearer " + f"{token}"
data = {}
data["uid"] = "89"
data["content"] = "texto de prueba del fichero"
reponse = requests.post(url, headers=headers, data=json.dumps(data))

if reponse.status_code == 404:
    print(" >>> [ERROR]: " + f"{reponse.json()} <<< ")
else:
    raise Exception(" >>> El test 1 debia devolver ERROR y devolvio [OK]: " + f"{reponse.json()} <<< ")

# Test 2: Crear archivo 'fichero_001.txt' con UID válido (usuario 'antonio')
# Debe devolver OK ya que el usuario es válido y autorizado.
print()
print("Creando archivo fichero_001.txt con el contenido 'texto de prueba del fichero' del usuario antonio...")
print("Debe devolver OK")
print()

url = URL_FILE + "create_file/fichero_001.txt"
headers = {}
headers["Content-Type"] = "application/json"
headers["Authorization"] = "Bearer " + f"{token}"
data = {}
data["uid"] = UID
data["content"] = "texto de prueba del fichero"
reponse = requests.post(url, headers=headers, data=json.dumps(data))

if reponse.status_code == 200:
    print(" >>> [OK]: " + f"{reponse.json()} <<< ")
else:
    raise Exception(" >>> El test 2 debia devolver OK y devolvio [ERROR]: " + f"{reponse.json()} <<< ")

# Test 3: Crear archivo 'fichero_002.txt' con contenido diferente
# Debe devolver OK al crear un nuevo archivo con un contenido diferente.
print()
print("Creando archivo fichero_002.txt con el contenido 'texto de prueba del fichero 2'")
print("Debe devolver OK")
print()

url = URL_FILE + "create_file/fichero_002.txt"
headers = {}
headers["Content-Type"] = "application/json"
headers["Authorization"] = "Bearer " + f"{token}"
data = {}
data["uid"] = UID
data["content"] = "texto de prueba del fichero"
reponse = requests.post(url, headers=headers, data=json.dumps(data))

if reponse.status_code == 200:
    print(" >>> [OK]: " + f"{reponse.json()} <<< ")
else:
    raise Exception(" >>> El test 3 debia devolver OK y devolvio [ERROR]: " + f"{reponse.json()} <<< ")

# Test 4: Listar archivos del usuario 'antonio'
# Debe devolver OK con una lista de los archivos 'fichero_001.txt' y 'fichero_002.txt'.
print()
print("Listando archivos del usuario antonio...")
print("Debe devolver OK y los archivos fichero_001.txt y fichero_002.txt")
print()

url = URL_FILE + "list_files"
headers = {}
headers["Content-Type"] = "application/json"
headers["Authorization"] = "Bearer " + f"{token}"
data = {}
data["uid"] = UID
reponse = requests.post(url, headers=headers, data=json.dumps(data))

if reponse.status_code == 200:
    print(" >>> [OK]: " + f"{reponse.json()} <<< ")
else:
    raise Exception(" >>> El test 4 debia devolver OK y devolvio [ERROR]: " + f"{reponse.json()} <<< ")

# Test 5: Eliminar el archivo 'fichero_001.txt'
# Debe devolver OK después de eliminar correctamente el archivo.
print()
print("Eliminando archivo fichero_001.txt...")
print("Debe devolver OK")
print()

url = URL_FILE + "delete_file/fichero_001.txt"
headers = {}
headers["Content-Type"] = "application/json"
headers["Authorization"] = "Bearer " + f"{token}"
data = {}
data["uid"] = UID
reponse = requests.post(url, headers=headers, data=json.dumps(data))

if reponse.status_code == 200:
    print(" >>> [OK]: " + f"{reponse.json()} <<< ")
else:
    raise Exception(" >>> El test 5 debia devolver OK y devolvio [ERROR]: " + f"{reponse.json()} <<< ")

# Test 6: Listar archivos después de eliminar 'fichero_001.txt'
# Debe devolver OK con solo 'fichero_002.txt' en la lista.
print()
print("Listando archivos del usuario antonio...")
print("Debe devolver OK y los archivos fichero_002.txt")
print()

url = URL_FILE + "list_files"
headers = {}
headers["Content-Type"] = "application/json"
headers["Authorization"] = "Bearer " + f"{token}"
data = {}
data["uid"] = UID
reponse = requests.post(url, headers=headers, data=json.dumps(data))

if reponse.status_code == 200:
    print(" >>> [OK]: " + f"{reponse.json()} <<< ")
else:
    raise Exception(" >>> El test 6 debia devolver OK y devolvio [ERROR]: " + f"{reponse.json()} <<< ")

# Test 7: Descargar el archivo 'fichero_001.txt' (que ya fue eliminado)
# Debe devolver ERROR ya que el archivo fue eliminado previamente.
print()
print("Descargando archivo fichero_001.txt...")
print("Debe devolver ERROR")
print()

url = URL_FILE + "download_file/fichero_001.txt"
headers = {}
headers["Content-Type"] = "application/json"
data = {}
data["uid"] = UID
reponse = requests.get(url, headers=headers, data=json.dumps(data))

if reponse.status_code != 200:
    print(" >>> [ERROR]: " + f"{reponse.json()} <<< ")
else:
    raise Exception(" >>> El test 7 debia devolver ERROR y devolvio [OK]: " + f"{reponse.json()} <<< ")

# Test 8: Descargar el archivo 'fichero_002.txt'
# Debe devolver OK al descargar correctamente el archivo.
print()
print("Descargando archivo fichero_002.txt...")
print("Debe devolver OK")
print()

url = URL_FILE + "download_file/fichero_002.txt"
headers = {}
headers["Content-Type"] = "application/json"
data = {}
data["uid"] = UID
reponse = requests.get(url, headers=headers, data=json.dumps(data))

if reponse.status_code == 200:
    print(" >>> OK: " + f"{reponse.json()} <<< ")
else:
    raise Exception(" >>> El test 8 debia devolver OK y devolvio [ERROR]: " + f"{reponse.json()} <<< ")

# Test 9: Leer el archivo 'fichero_001.txt' (que ya fue eliminado)
# Debe devolver ERROR ya que el archivo fue eliminado.
print()
print("Leyendo archivo fichero_001.txt...")
print("Debe devolver ERROR")
print()

url = URL_FILE + "read_file/fichero_001.txt"
headers = {}
headers["Content-Type"] = "application/json"
data = {}
data["uid"] = UID
reponse = requests.post(url, headers=headers, data=json.dumps(data))

if reponse.status_code != 200:
    print(" >>> [ERROR]: " + f"{reponse.json()} <<< ")
else:
    raise Exception(" >>> El test 9 debia devolver ERROR y devolvio [OK]: " + f"{reponse.json()} <<< ")

# Test 10: Leer el archivo 'fichero_002.txt'
# Debe devolver OK al leer correctamente el archivo.
print()
print("Leyendo archivo fichero_002.txt...")
print("Debe devolver OK")
print()

url = URL_FILE + "read_file/fichero_002.txt"
headers = {}
headers["Content-Type"] = "application/json"
data = {}
data["uid"] = UID
reponse = requests.post(url, headers=headers, data=json.dumps(data))

if reponse.status_code == 200:
    print(" >>> OK: " + f"{reponse.json()} <<< ")
else:
    raise Exception(" >>> El test 10 debia devolver OK y devolvio [ERROR]: " + f"{reponse.json()} <<< ")

# Test 11: Modificar archivo 'fichero_002.txt' con contenido diferente
# Debe devolver OK al modificar el archivo correctamente.
print()
print("modificandp archivo fichero_002.txt con el contenido 'hemos cambiado el contenido del fichero'")
print("Debe devolver OK")
print()

url = URL_FILE + "create_file/fichero_002.txt"
headers = {}
headers["Content-Type"] = "application/json"
headers["Authorization"] = "Bearer " + f"{token}"
data = {}
data["uid"] = UID
data["content"] = "hemos cambiado el contenido del fichero"
reponse = requests.post(url, headers=headers, data=json.dumps(data))

if reponse.status_code == 200:
    print(" >>> [OK]: " + f"{reponse.json()} <<< ")
else:
    raise Exception(" >>> El test 11 debia devolver OK y devolvio [ERROR]: " + f"{reponse.json()} <<< ")

# Test 12: Leer el archivo 'fichero_002.txt'
# Debe devolver OK al leer correctamente el archivo con el contenido nuevo.
print()
print("Leyendo archivo fichero_002.txt...")
print("Debe devolver OK")
print()

url = URL_FILE + "read_file/fichero_002.txt"
headers = {}
headers["Content-Type"] = "application/json"
data = {}
data["uid"] = UID
reponse = requests.post(url, headers=headers, data=json.dumps(data))

if reponse.status_code == 200:
    print(" >>> OK: " + f"{reponse.json()} <<< ")
else:
    raise Exception(" >>> El test 12 debia devolver OK y devolvio [ERROR]: " + f"{reponse.json()} <<< ")

# Finaliza el test de file.py
print()
print(" >>> TERMINA EL TEST DE file.py <<< ")
print()

print (" >>> TODOS LOS TESTS HAN SIDO CORRECTOS <<< ")
print()

# Limpieza del servidor de archivos y usuarios
print ("Eliminando usuarios y archivos creados... ")
print()

# Eliminar 'fichero_002.txt
url = URL_FILE + "delete_file/fichero_002.txt"
headers = {}
headers["Content-Type"] = "application/json"
headers["Authorization"] = "Bearer " + f"{token}"
data = {}
data["uid"] = UID
reponse = requests.post(url, headers=headers, data=json.dumps(data))

if reponse.status_code == 200:
    print(" >>> [OK]: " + f"{reponse.json()} <<< ")
else:
    print(" >>> [ERROR]: " + f"{reponse.json()} <<< ")

# Eliminar el usuario 'antonio'
url = URL_USER + "delete_user"
headers = {}
headers["Content-Type"] = "application/json"
headers["Authorization"] = "Bearer " + f"{token}"
data = {}
data["uid"] = UID
reponse = requests.post(url, headers=headers, data=json.dumps(data))

if reponse.status_code == 200:
    print(" >>> [OK]: " + f"{reponse.json()} <<< ")
else:
    print(" >>> [ERROR]: " + f"{reponse.json()} <<< ")

print()
print (" >>> FIN DE LOS TEST <<< ")
print()