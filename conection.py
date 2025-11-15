import json
import os

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# ====================================================================
#              ⚙️  CONFIGURACIÓN DESDE ARCHIVO .env
# ====================================================================
# 1. Obtiene la URI (Endpoint) de la variable de entorno
HOST = os.getenv("COSMOS_DB_HOST")
# 2. Obtiene la PRIMARY KEY de la variable de entorno
KEY = os.getenv("COSMOS_DB_KEY")

# 3. Nombres de la Base de Datos y Contenedor desde variables de entorno
DATABASE_ID = os.getenv("COSMOS_DB_DATABASE_ID")
CONTAINER_ID = os.getenv("COSMOS_DB_CONTAINER_ID")
# ====================================================================

# Validar que las variables de entorno se cargaron correctamente
if not all([HOST, KEY, DATABASE_ID, CONTAINER_ID]):
    print("❌ Error: Faltan una o más variables de entorno en el archivo .env.")
    print(
        "   Asegúrate de que COSMOS_DB_HOST, COSMOS_DB_KEY, COSMOS_DB_DATABASE_ID, y COSMOS_DB_CONTAINER_ID están definidos."
    )
    exit()

# Inicializar el cliente de Cosmos DB
client = cosmos_client.CosmosClient(HOST, {"masterKey": KEY})

print("--- Iniciando Conexión a Azure Cosmos DB ---")

try:
    # 1. Obtener referencia a la Base de Datos y al Contenedor
    database = client.get_database_client(DATABASE_ID)
    container = database.get_container_client(CONTAINER_ID)

    print(
        f"✅ Conexión exitosa a la Base de Datos: {DATABASE_ID} y Contenedor: {CONTAINER_ID}\n"
    )

    # 2. Insertar/Actualizar algunos datos de ejemplo (Items)
    print("➡️  Paso 1: Insertando ítems de ejemplo en el Contenedor 'Productos'...")
    items_a_insertar = [
        {
            "id": "P001",
            "nombre": "Laptop Gamer",
            "categoria": "Electronicos",
            "precio": 1200.00,
        },
        {
            "id": "P002",
            "nombre": "Teclado Mecánico",
            "categoria": "Perifericos",
            "precio": 95.50,
        },
        {
            "id": "P003",
            "nombre": "Monitor Curvo 27",
            "categoria": "Electronicos",
            "precio": 450.00,
        },
    ]

    for item in items_a_insertar:
        # Se usa upsert_item para insertar si no existe, o actualizar si ya tiene el mismo ID
        container.upsert_item(body=item)
        print(f"   - Ítem procesado: {item['nombre']} ({item['categoria']})")

    # 3. Consultar y listar todos los datos del contenedor (REQUISITO DEL LABORATORIO)
    print(
        "\n📜 Paso 2: Consultando y Listando todos los datos del contenedor 'Productos':"
    )

    # Consulta SQL para la API de Núcleo (Core SQL)
    query = "SELECT c.id, c.nombre, c.precio, c.categoria FROM c"

    # Ejecutar la consulta. enable_cross_partition_query es útil si la consulta
    # no incluye la clave de partición, aunque es menos eficiente para grandes volúmenes.
    items_listados = container.query_items(
        query=query, enable_cross_partition_query=True
    )

    # Imprimir los resultados
    print("-" * 50)
    for item in items_listados:
        # Usamos json.dumps para formatear la salida como JSON (si es necesario)
        # Aquí lo formateamos para una lectura clara:
        print(
            f"| ID: {item['id']} | Nombre: {item['nombre']} | Precio: S/. {item['precio']:.2f} | Categoría: {item['categoria']} |"
        )
    print("-" * 50)

    print("\n✅ Script finalizado con éxito.")

except exceptions.CosmosHttpResponseError as e:
    # Captura errores específicos de Cosmos DB (ej. clave incorrecta, BD no existe)
    print(f"\n❌ Error de Conexión o Respuesta de Cosmos DB (Código: {e.status_code}):")
    print(f"   Mensaje: {e.message}")
    print(
        "   Verifica que la HOST y KEY sean correctas, y que la BD y Contenedor existan."
    )
except Exception as e:
    # Captura otros errores generales (ej. errores de sintaxis o conexión local)
    print(f"\n❌ Ocurrió un error inesperado durante la ejecución: {e}")
