import os
import json
import uuid
import hashlib
from quart import Quart, request, jsonify

app = Quart(__name__)

# Conocer el entorno en el que se está ejecutando la aplicación
RUNNING_IN_DOCKER = os.environ.get('DOCKER_ENV', False)

if RUNNING_IN_DOCKER:
    USER_DIR = "/app/users" # Si se ejecuta en Docker la ruta de usuarios se encuentra en el volumen compartido /app/users
else:
    USER_DIR = "../user_service/users/" # Si se ejecuta en local la ruta de usuarios se encuentra en la carpeta user_service

SECRET_UUID = uuid.UUID('00010203-0405-0607-0809-0a0b0c0d0e0f')

os.makedirs(USER_DIR, exist_ok=True)

def hash_password(password):
    """
    Crea un hash seguro para la contraseña del usuario utilizando SHA256 y un salt basado en SECRET_UUID.
    Args:
        password (str): La contraseña del usuario en texto plano.
    Returns:
        str: El hash de la contraseña.
    """
    salt = SECRET_UUID.bytes
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return hashed_password.hex()

def verify_password(password, stored_password):
    """
    Verifica si la contraseña proporcionada coincide con el hash almacenado.
    Args:
        password (str): Contraseña en texto plano ingresada por el usuario.
        stored_password (str): Hash de la contraseña almacenado.
    Returns:
        bool: (bool) True si la contraseña es correcta, False en caso contrario.
    """
    salt = SECRET_UUID.bytes
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return hashed_password.hex() == stored_password

def create_token(uid, secret):
    """
    Genera un token único para el usuario basado en su UID y un UUID secreto.
    Args:
        uid (str): El ID único del usuario.
        secret (UUID): El UUID secreto para generar el token.
    Returns:
        str: El token generado.
    """
    token_hash = uuid.uuid5(secret, uid)
    return f"{token_hash}"

# Funcion para validar token de usuario
def validate_token(uid, token, secret):
    """
    Valida si el token proporcionado coincide con el token esperado.
    Args:
        uid (str): El ID único del usuario.
        token (str): El token proporcionado.
        secret (UUID): El UUID secreto para verificar el token.
    Returns:
        bool: True si el token es válido, False si no lo es.
    """
    expected_token = create_token(uid, secret)
    return token == expected_token

# Funcion para obtener datos de usuario
def get_user_data(uid):
    """
    Busca los datos de un usuario basado en su UID.
    Args:
        uid (str): El ID único del usuario.
    Returns:
        dict: Los datos del usuario si se encuentra, None si no.
    """
    for filename in os.listdir(USER_DIR):
        if filename.endswith(".json"):
            user_file = os.path.join(USER_DIR, filename)
            with open(user_file, 'r') as f:
                user_data = json.load(f)
                if user_data['uid'] == uid:
                    return user_data
    return None

# Creación de usuario
@app.post('/create_user/<name>')
async def create_user(name):
    """
    Endpoint para crear un nuevo usuario.
    Args:
        name (str): El nombre del usuario (parte de la URL).
    Request JSON:
        - password (str): La contraseña del usuario.
    Returns:
        JSON: Mensaje de éxito con UID y token, o error si ya existe.
    """
    data = await request.get_json()
    password = data.get('password')
    
    if not name or not password:
        return jsonify({"Error": "Name and password required"}), 400
    
    user_file = f"{USER_DIR}/{name}.json"
    if os.path.exists(user_file):
        return jsonify({"Error": "User already exists"}), 409
    
    # Comprueba si el usuario ya existe
    uid = str(uuid.uuid4())
    token = create_token(uid, SECRET_UUID)
    hashed_password = hash_password(password)

    # Guarda los datos del usuario 
    user_data = {
        "name": name,
        "password": hashed_password,
        "uid": uid,
        "token": token
    }

    with open(f"{USER_DIR}/{name}.json", "w") as f:
        f.write(json.dumps(user_data))
    
    return jsonify({"message": "User succesfuly created","uid": uid, "token": token}), 200

# Delete de usuario
@app.post('/delete_user')
async def delete_user():
    """
    Endpoint para eliminar un usuario basado en su UID.
    Request Headers:
        - Authorization: Bearer <token>
    Request JSON:
        - uid (str): El ID único del usuario.
    Returns:
        JSON: Mensaje de éxito o error si no se encuentra el usuario.
    """
    if request.headers.get('Authorization', '').split(' ')[0] == 'Bearer':
        token = request.headers.get('Authorization', '').split(' ')[-1]
    else:
        return jsonify({"Error": "Format must be \"Authorization Bearer <token>\""}), 405

    data = await request.get_json()
    uid = data.get('uid')
    
    user_data = get_user_data(uid)
    if not user_data:
        return jsonify({"Error": "User not found"}), 404
    
    if not validate_token(uid, token, SECRET_UUID):
        return jsonify({"Error": "Unvalid token"}), 403
    
    user_file = f"{USER_DIR}/{user_data['name']}.json"
    if os.path.exists(user_file):
        os.remove(user_file)
    else:
        return jsonify({"Error": f"File {user_file} not found"}), 404
    
    return jsonify({"Success": f"User {user_data['name']} deleted"}), 200
    

# Modificacion de contraseña
@app.put('/update_password')
async def update_paswd():
    """
    Endpoint para actualizar la contraseña de un usuario.
    Request Headers:
        - Authorization: Bearer <token>
    Request JSON:
        - uid (str): El ID único del usuario.
        - password (str): La nueva contraseña.
    Returns:
        JSON: Mensaje de éxito o error si ocurre algún problema.
    """
    if request.headers.get('Authorization', '').split(' ')[0] == 'Bearer':
        token = request.headers.get('Authorization', '').split(' ')[-1]
    else:
        return jsonify({"Error": "Format must be \"Authorization Bearer <token>\""}), 405

    data = await request.get_json()
    uid = data.get('uid')
    password = data.get('password')
    
    if not password or not uid:
        return jsonify({"Error": "Password and UID required"}), 400
    
    user_data = get_user_data(uid)
    if not user_data:
        return jsonify({"Error": "User not found"}), 404
    
    if not validate_token(uid, token, SECRET_UUID):
        return jsonify({"Error": "Unvalid token"}), 403
    
    stored_password = user_data['password']
    
    try:
        user_file = f"{USER_DIR}/{user_data['name']}.json"
        user_data['password'] = hash_password(password)
        with open(user_file, 'w') as f:
            f.write(json.dumps(user_data))
        
        return jsonify({"Success": f"Password updated"}), 200
    except Exception as e:
        return jsonify({"Error": str(e)}), 500
    

# Log in de usuario
@app.post('/get_user_uid/<name>')
async def login_user(name):
    """
    Endpoint para iniciar sesión con el nombre del usuario.
    Args:
        name (str): El nombre del usuario (parte de la URL).
    Request JSON:
        - password (str): La contraseña del usuario.
    Returns:
        JSON: El UID y token si las credenciales son correctas, o un error si no lo son.
    """
    data = await request.get_json()
    password = data.get('password')
    
    if not name or not password:
        return jsonify({"Error": "Name and password required"}), 400

    #Comprueba si el usuario existe
    user_file = f"{USER_DIR}/{name}.json"
    if not os.path.exists(user_file):
        return jsonify({"Error": "Invalid name"}), 404
    
    with open(user_file, "r") as f:
        user_data = json.loads(f.read())
    

    if user_data['name'] == name and verify_password(password, user_data['password']):
        return jsonify({"uid": user_data["uid"], "token": user_data["token"]}), 200
    else:
        return jsonify({"Error": f"Invalid password"}), 401
   
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)

'''
Comprobacion:

python3 user.py

Creacion de usuario:
curl -X POST http://0.0.0.0:5050/create_user/Blanca -H 'Content-Type: application/json' -d '{"password": "Prueba123"}'

Inicio sesion:
curl -X POST http://0.0.0.0:5050/get_user_uid/Blanca -H 'Content-Type: application/json' -d '{"password": "Prueba123"}'

Borrar usuario:
curl -X POST http://0.0.0.0:5050/delete_user -H 'Content-Type: application/json' --H 'Authorization: Bearer ' -d '{"uid": ""}'

Actualizar contraseña:
curl -X PUT http://0.0.0.0:5050/update_password -H 'Content-Type: application/json' -H 'Authorization: Bearer ' -d '{"uid": "", "password": "123456"}'

'''