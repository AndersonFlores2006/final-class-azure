import json
import os
import uuid

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for

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
    categories = []
    error_message = None

    if _cosmos_client is None:
        error_message = "Error de configuración: Las variables de entorno de Cosmos DB no están definidas."
        return render_template("index.html", error=error_message)

    try:
        database = _cosmos_client.get_database_client(DATABASE_ID)
        container = database.get_container_client(CONTAINER_ID)

        # Obtener todos los productos
        query_products = "SELECT c.id, c.nombre, c.categoria, c.precio FROM c"
        items_listados = container.query_items(
            query=query_products, enable_cross_partition_query=True
        )
        products = list(items_listados)

        # Obtener todas las categorías únicas
        query_categories = "SELECT DISTINCT c.categoria FROM c"
        category_items = container.query_items(
            query=query_categories, enable_cross_partition_query=True
        )
        categories = [item['categoria'] for item in category_items]

    except exceptions.CosmosHttpResponseError as e:
        error_message = (
            f"Error de Cosmos DB (Código: {e.status_code}): {e.message}. "
            "Verifica tu HOST y KEY, y que la BD y Contenedor existan."
        )
    except Exception as e:
        error_message = f"Ocurrió un error inesperado: {e}"

    return render_template("index.html", products=products, categories=categories, error=error_message)


@app.route("/add", methods=["POST"])
def add_product():
    if _cosmos_client is None:
        return redirect(url_for("list_products"))

    try:
        database = _cosmos_client.get_database_client(DATABASE_ID)
        container = database.get_container_client(CONTAINER_ID)

        new_product = {
            "id": str(uuid.uuid4()),
            "nombre": request.form["nombre"],
            "categoria": request.form["categoria"],
            "precio": float(request.form["precio"]),
        }

        container.create_item(body=new_product)

    except exceptions.CosmosHttpResponseError as e:
        # Manejar error, por ejemplo, mostrar un mensaje al usuario
        print(f"Error al agregar producto: {e.message}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

    return redirect(url_for("list_products"))


@app.route("/edit/<item_id>/<category>")
def edit_product_form(item_id, category):
    if _cosmos_client is None:
        return redirect(url_for("list_products"))

    product = None
    categories = []
    error_message = None
    
    try:
        database = _cosmos_client.get_database_client(DATABASE_ID)
        container = database.get_container_client(CONTAINER_ID)
        
        # Obtener el producto a editar
        product = container.read_item(item=item_id, partition_key=category)

        # Obtener todas las categorías para el desplegable
        query_categories = "SELECT DISTINCT c.categoria FROM c"
        category_items = container.query_items(
            query=query_categories, enable_cross_partition_query=True
        )
        categories = [item['categoria'] for item in category_items]

    except exceptions.CosmosHttpResponseError as e:
        if e.status_code == 404:
            error_message = "Producto no encontrado."
        else:
            error_message = f"Error de Cosmos DB: {e.message}"
    except Exception as e:
        error_message = f"Ocurrió un error: {e}"

    return render_template("edit.html", product=product, categories=categories, error=error_message)


@app.route("/update/<item_id>", methods=["POST"])
def update_product(item_id):
    if _cosmos_client is None:
        return redirect(url_for("list_products"))

    try:
        database = _cosmos_client.get_database_client(DATABASE_ID)
        container = database.get_container_client(CONTAINER_ID)

        updated_product = {
            "id": item_id,
            "nombre": request.form["nombre"],
            "categoria": request.form["categoria"],
            "precio": float(request.form["precio"]),
        }
        
        # upsert_item reemplazará el documento si ya existe
        container.upsert_item(body=updated_product)

    except Exception as e:
        print(f"Error al actualizar producto: {e}")

    return redirect(url_for("list_products"))


@app.route("/delete/<item_id>/<category>", methods=["POST"])
def delete_product(item_id, category):
    if _cosmos_client is None:
        return redirect(url_for("list_products"))

    try:
        database = _cosmos_client.get_database_client(DATABASE_ID)
        container = database.get_container_client(CONTAINER_ID)
        
        container.delete_item(item=item_id, partition_key=category)

    except Exception as e:
        print(f"Error al eliminar producto: {e}")

    return redirect(url_for("list_products"))


if __name__ == "__main__":
    # Para ejecutar en un entorno de desarrollo, Flask usa un servidor ligero.
    # NO USAR en producción.
    # host='0.0.0.0' permite que sea accesible desde otras máquinas en la red.
    app.run(debug=True, host="0.0.0.0")
