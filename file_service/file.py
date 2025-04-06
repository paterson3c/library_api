from quart import Quart, request, jsonify, Response
import os
import uuid
import json

app = Quart(__name__)

# Conocer el entorno en el que se está ejecutando la aplicación
RUNNING_IN_DOCKER = os.environ.get('DOCKER_ENV', False)

if RUNNING_IN_DOCKER:
    USER_DIR = "/app/users" # Si se ejecuta en Docker la ruta de usuarios se encuentra en el volumen compartido /app/users
else:
    USER_DIR = "../user_service/users/" # Si se ejecuta en local la ruta de usuarios se encuentra en la carpeta user_service

LIBRARY_DIR = "./libraries"  # Directorio donde se almacenan los archivos
SECRET_UUID = uuid.UUID('00010203-0405-0607-0809-0a0b0c0d0e0f')  # UUID secreto

# Crear el directorio para las bibliotecas si no existe
os.makedirs(LIBRARY_DIR, exist_ok=True)

def create_token(uid: str, secret: uuid.UUID) -> str:
    """
    Genera un token basado en el UUID del usuario y un UUID secreto.

    Args:
        uid (str): El ID único del usuario.
        secret (UUID): El UUID secreto para generar el token.

    Returns:
        str: Token generado.
    """
    token_hash = uuid.uuid5(secret, uid)
    return f"{token_hash}"

def validate_token(token: str, expected_token: str) -> bool:
    """
    Valida si el token proporcionado coincide con el token esperado.

    Args:
        token (str): Token proporcionado.
        expected_token (str): Token esperado para validación.

    Returns:
        bool: True si los tokens coinciden, False si no.
    """
    return token == expected_token

def get_user(uid: str) -> bool:
    """
    Verifica si existe un usuario con el UID proporcionado en el directorio de usuarios.

    Args:
        uid (str): El ID único del usuario.

    Returns:
        bool: True si el usuario existe, False si no.
    """
    for filename in os.listdir(USER_DIR):
        if filename.endswith(".json"):
            user_file = os.path.join(USER_DIR, filename)
            with open(user_file, 'r') as f:
                user_data = json.load(f)
                if user_data['uid'] == uid:
                    return True
    return False

# Endpoint para crear o actualizar un archivo
@app.post('/create_file/<filename>')
async def create_file(filename: str):
    """
    Crea o actualiza un archivo en la biblioteca del usuario.

    Request Headers:
        - Authorization: Bearer <token>

    Request JSON:
        - uid (str): El ID del usuario.
        - content (str): El contenido del archivo.

    Args:
        filename (str): El nombre del archivo a crear.

    Returns:
        JSON: Mensaje de éxito o error.
    """
    if request.headers.get('Authorization', '').split(' ')[0] == 'Bearer':
        token = request.headers.get('Authorization', '').split(' ')[-1]
    else:
        return jsonify({"Error": "Format must be \"Authorization Bearer <token>\""}), 405

    data = await request.get_json()
    uid = data.get('uid')
    content = data.get('content')
    
    if not filename or not uid or not content:
        return jsonify({"Error": "Filename, uid and content required"}), 400
    
    if not get_user(uid):
        return jsonify({"Error": "User not found"}), 404
    
    if not validate_token(token, create_token(uid, SECRET_UUID)):
        return jsonify({"Error": "Invalid token"}), 403
    
    # Crear directorio del usuario si no existe
    user_library_dir = os.path.join(LIBRARY_DIR, uid)
    os.makedirs(user_library_dir, exist_ok=True)

    # Guardar el archivo
    file_path = os.path.join(user_library_dir, filename)
    with open(file_path, 'wb') as f:
        f.write(content.encode('utf-8'))
    
    return jsonify({"message": f"File '{filename}' uploaded successfully"}), 200

# Endpoint para borrar un archivo
@app.post('/delete_file/<filename>')
async def delete_file(filename: str):
    """
    Elimina un archivo en la biblioteca del usuario.

    Request Headers:
        - Authorization: Bearer <token>

    Request JSON:
        - uid (str): El ID del usuario.

    Args:
        filename (str): El nombre del archivo a eliminar.

    Returns:
        JSON: Mensaje de éxito o error.
    """
    if request.headers.get('Authorization', '').split(' ')[0] == 'Bearer':
        token = request.headers.get('Authorization', '').split(' ')[-1]
    else:
        return jsonify({"Error": "Format must be \"Authorization Bearer <token>\""}), 405
    
    data = await request.get_json()
    uid = data.get('uid')
    
    if not filename or not uid or not token:
        return jsonify({"Error": "Filename, uid and token required"}), 400
    
    if not get_user(uid):
        return jsonify({"Error": "User not found"}), 404
    
    if not validate_token(token, create_token(uid, SECRET_UUID)):
        return jsonify({"Error": "Invalid token"}), 403
    
    user_library_dir = os.path.join(LIBRARY_DIR, uid)
    file_path = os.path.join(user_library_dir, filename)
    
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({"message": f"File '{filename}' deleted successfully"}), 200
    else:
        return jsonify({"Error": "File not found"}), 404

# Endpoint para listar los archivos de un usuario
@app.post('/list_files')
async def list_files():
    """
    Lista los archivos en la biblioteca del usuario.

    Request Headers:
        - Authorization: Bearer <token>

    Request JSON:
        - uid (str): El ID del usuario.

    Returns:
        JSON: Lista de archivos o error.
    """
    if request.headers.get('Authorization', '').split(' ')[0] == 'Bearer':
        token = request.headers.get('Authorization', '').split(' ')[-1]
    else:
        return jsonify({"Error": "Format must be \"Authorization Bearer <token>\""}), 405
    
    data = await request.get_json()
    uid = data.get('uid')

    if not uid:
        return jsonify({"Error": "Uid required"}), 400
    
    if not get_user(uid):
        return jsonify({"Error": "User not found"}), 404
    
    if not validate_token(token, create_token(uid, SECRET_UUID)):
        return jsonify({"Error": "Invalid token"}), 403
    
    # Listar archivos en el directorio de la biblioteca del usuario
    user_library_dir = os.path.join(LIBRARY_DIR, uid)
    files = os.listdir(user_library_dir)

    return jsonify({"files": files}), 200

# Endpoint para descargar un archivo
@app.get('/download_file/<filename>')
async def download_file(filename: str):
    """
    Descarga un archivo de la biblioteca del usuario.

    Request JSON:
        - uid (str): El ID del usuario.

    Args:
        filename (str): El nombre del archivo a descargar.

    Returns:
        JSON: Mensaje de éxito o error.
    """
    data = await request.get_json()
    uid = data.get('uid')

    if not filename or not uid:
        return jsonify({"Error": "Filename and uid of the library required"}), 400
    
    if not get_user(uid):
        return jsonify({"Error": "Library not found"}), 404
    
    user_library_dir = os.path.join(LIBRARY_DIR, uid)
    file_path = os.path.join(user_library_dir, filename)

    if os.path.exists(file_path):
        os.makedirs('../downloads', exist_ok=True)
        with open(file_path, 'rb') as f:
            file_content = f.read()
        file_path = os.path.join('../downloads', filename)
        with open(file_path, 'wb') as f:
            f.write(file_content)
        return jsonify({"message": f"File '{filename}' downloaded successfully"}), 200
    else:
        return jsonify({"Error": "File not found"}), 404

# Endpoint para leer el contenido de un archivo
@app.post('/read_file/<filename>')
async def read_file(filename: str):
    """
    Lee el contenido de un archivo de la biblioteca del usuario.

    Request JSON:
        - uid (str): El ID del usuario.

    Args:
        filename (str): El nombre del archivo a leer.

    Returns:
        JSON: Contenido del archivo o error.
    """
    data = await request.get_json()
    uid = data.get('uid')

    if not filename or not uid:
        return jsonify({"Error": "Filename and uid of the library required"}), 400
    
    if not get_user(uid):
        return jsonify({"Error": "Library not found"}), 404
    
    user_library_dir = os.path.join(LIBRARY_DIR, uid)
    file_path = os.path.join(user_library_dir, filename)

    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            file_content = f.read()
        return jsonify({f"Reading file '{filename}'":  f"    {file_content}    "}), 200
    else:
        return jsonify({"Error": "File not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5051)

"""
Comprobacion

curl -X POST http://127.0.0.1:5051/create_file/prueba.txt -H 'Content-Type: application/json'  -H 'Authorization: Bearer' -d '{"uid": "", "content": "texto de prueba del fichero"}'
curl -X POST http://127.0.0.1:5051/delete_file/prueba.txt -H 'Content-Type: application/json' -H 'Authorization: Bearer ' -d '{"uid": ""}'
curl -X POST http://127.0.0.1:5051/list_files -H 'Content-Type: application/json' -H 'Authorization: Bearer ' -d '{"uid": ""}'
curl -X GET http://127.0.0.1:5051/download_file/prueba.txt -H 'Content-Type: application/json' -d '{"uid": ""}'

"""