import json
import os

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from dotenv import load_dotenv
from flask import Flask, render_template

app = Flask(__name__)

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# ====================================================================
#              ⚙️  CONFIGURACIÓN DESDE ARCHIVO .env
# ====================================================================
HOST = os.getenv("COSMOS_DB_HOST")
KEY = os.getenv("COSMOS_DB_KEY")
DATABASE_ID = os.getenv("COSMOS_DB_DATABASE_ID")
CONTAINER_ID = os.getenv("COSMOS_DB_CONTAINER_ID")
# ====================================================================

# Validar que las variables de entorno se cargaron correctamente
if not all([HOST, KEY, DATABASE_ID, CONTAINER_ID]):
    print("❌ Error: Faltan una o más variables de entorno en el archivo .env.")
    print(
        "   Asegúrate de que COSMOS_DB_HOST, COSMOS_DB_KEY, COSMOS_DB_DATABASE_ID, y COSMOS_DB_CONTAINER_ID están definidos."
    )
    # En una aplicación web, no queremos salir, sino manejar el error de forma más elegante
    # Por ahora, imprimimos y usaremos un error en la UI.
    _cosmos_client = None
else:
    # Inicializar el cliente de Cosmos DB
    _cosmos_client = cosmos_client.CosmosClient(HOST, {"masterKey": KEY})


@app.route("/")
def list_products():
    products = []
    error_message = None

    if _cosmos_client is None:
        error_message = "Error de configuración: Las variables de entorno de Cosmos DB no están definidas."
        return render_template("index.html", error=error_message)

    try:
        database = _cosmos_client.get_database_client(DATABASE_ID)
        container = database.get_container_client(CONTAINER_ID)

        query = "SELECT c.id, c.nombre, c.categoria, c.precio FROM c"
        items_listados = container.query_items(
            query=query, enable_cross_partition_query=True
        )

        for item in items_listados:
            products.append(item)

    except exceptions.CosmosHttpResponseError as e:
        error_message = (
            f"Error de Cosmos DB (Código: {e.status_code}): {e.message}. "
            "Verifica tu HOST y KEY, y que la BD y Contenedor existan."
        )
    except Exception as e:
        error_message = f"Ocurrió un error inesperado: {e}"

    return render_template("index.html", products=products, error=error_message)


if __name__ == "__main__":
    # Para ejecutar en un entorno de desarrollo, Flask usa un servidor ligero.
    # NO USAR en producción.
    # host='0.0.0.0' permite que sea accesible desde otras máquinas en la red.
    app.run(debug=True, host="0.0.0.0")
