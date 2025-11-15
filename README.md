# Aplicación Flask con Azure Cosmos DB

Esta es una aplicación web simple desarrollada con Flask en Python que se conecta a Azure Cosmos DB para listar productos. Las credenciales de la base de datos se gestionan a través de variables de entorno para una mayor seguridad.

## Estructura del Proyecto

- `conection.py`: Script original para la conexión y manipulación de datos en Cosmos DB (ahora utiliza variables de entorno).
- `app.py`: La aplicación web Flask que consulta Cosmos DB y renderiza los resultados.
- `templates/index.html`: Plantilla HTML para mostrar el listado de productos.
- `.env`: Archivo para almacenar las credenciales de Azure Cosmos DB (IGNORADO por Git).
- `requirements.txt`: Lista de dependencias de Python necesarias.
- `.gitignore`: Configuración para que Git ignore archivos y directorios como `.env` y `venv/`.

## Configuración Local

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/AndersonFlores2006/final-class-azure.git
    cd final-class-azure
    ```

2.  **Crea y activa un entorno virtual (opcional pero recomendado):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Linux/macOS
    # venv\Scripts\activate   # En Windows
    ```

3.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configura tus variables de entorno:**
    Crea un archivo llamado `.env` en la raíz del proyecto y añade tus credenciales de Azure Cosmos DB. **Asegúrate de reemplazar los valores de ejemplo con tus credenciales reales.**

    ```ini
    COSMOS_DB_HOST="https://tu-cuenta-cosmosdb.documents.azure.com:443/"
    COSMOS_DB_KEY="TU_PRIMARY_KEY_DE_AZURE_COSMOS_DB_AQUI"
    COSMOS_DB_DATABASE_ID="MiBaseDeDatos"
    COSMOS_DB_CONTAINER_ID="Productos"
    ```

5.  **Ejecuta la aplicación Flask:**
    ```bash
    python app.py
    ```
    La aplicación estará disponible en `http://127.0.0.1:5000/`.

## Cómo Ejecutar la Aplicación Localmente

Una vez que hayas completado los pasos de "Configuración Local" (instalación de dependencias y configuración del archivo `.env`), puedes iniciar la aplicación web Flask con el siguiente comando:

```bash
python app.py
```

Después de ejecutarlo, verás un mensaje en tu terminal indicando que el servidor web está en funcionamiento. Podrás acceder a la aplicación desde tu navegador web, generalmente en:

`http://127.0.0.1:5000/`

Abre esta URL en tu navegador para ver el listado de productos obtenidos de Azure Cosmos DB.

## Despliegue en Azure App Service con Azure CLI

Para desplegar esta aplicación en Azure App Service utilizando la interfaz de línea de comandos de Azure (Azure CLI), sigue estos pasos:

### Prerrequisitos

*   Una cuenta de Azure activa.
*   Azure CLI instalado ([Guía de instalación](https://docs.microsoft.com/es-es/cli/azure/install-azure-cli)).
*   Haber iniciado sesión en Azure CLI: `az login`.
*   Tu código de aplicación subido a un repositorio de GitHub (este repositorio).

### Pasos de Despliegue

1.  **Establecer Variables de Entorno (en tu terminal local):**
    Reemplaza los valores con los de tu cuenta de Azure y GitHub.

    ```bash
    RG_NAME="mi-grupo-recursos-cosmosdb"          # Nombre de tu Grupo de Recursos
    APP_SERVICE_NAME="mi-app-flask-cosmosdb-unique" # Nombre único para tu App Service
    LOCATION="eastus"                             # Región de Azure (ej. westus2, centralus)
    PYTHON_VERSION="Python|3.11"                  # Versión de Python
    GH_REPO_URL="https://github.com/AndersonFlores2006/final-class-azure.git"
    GH_BRANCH="master"

    # Credenciales de Cosmos DB (¡NO SUBAS ESTAS CLAVES A GIT!)
    COSMOS_HOST="https://tu-cuenta-cosmosdb.documents.azure.com:443/"
    COSMOS_KEY="TU_PRIMARY_KEY_DE_AZURE_COSMOS_DB_AQUI"
    COSMOS_DB_ID="MiBaseDeDatos"
    COSMOS_CONTAINER_ID="Productos"
    ```

2.  **Crear un Grupo de Recursos (si no tienes uno):**
    ```bash
    az group create --name $RG_NAME --location $LOCATION
    ```

3.  **Crear un Plan de App Service:**
    Un plan de App Service define los recursos de cómputo para tu aplicación. `B1` es un buen punto de partida para desarrollo/pruebas.

    ```bash
    az appservice plan create --name "${APP_SERVICE_NAME}-plan" --resource-group $RG_NAME --is-linux --sku B1
    ```

4.  **Crear la Aplicación Web de Azure App Service:**
    ```bash
    az webapp create --resource-group $RG_NAME --plan "${APP_SERVICE_NAME}-plan" --name $APP_SERVICE_NAME --runtime $PYTHON_VERSION
    ```

5.  **Configurar Variables de Entorno para Cosmos DB en App Service:**
    Estas configuraciones reemplazan tu archivo `.env` en el entorno de Azure.

    ```bash
    az webapp config appsettings set --resource-group $RG_NAME --name $APP_SERVICE_NAME --settings \
        COSMOS_DB_HOST="$COSMOS_HOST" \
        COSMOS_DB_KEY="$COSMOS_KEY" \
        COSMOS_DB_DATABASE_ID="$COSMOS_DB_ID" \
        COSMOS_DB_CONTAINER_ID="$COSMOS_CONTAINER_ID"
    ```

6.  **Configurar el Comando de Inicio de la Aplicación (Gunicorn):**
    App Service necesita saber cómo iniciar tu aplicación Flask. `gunicorn` es un servidor WSGI recomendado para producción.

    ```bash
    az webapp config set --resource-group $RG_NAME --name $APP_SERVICE_NAME --startup-file "gunicorn --bind 0.0.0.0 --worker-class gevent --workers 4 app:app"
    ```
    *Nota: Asegúrate de que `gunicorn` y `gevent` estén incluidos en tu `requirements.txt`.*

7.  **Configurar el Despliegue Continuo desde GitHub:**
    Esto vinculará tu App Service a tu repositorio de GitHub para que los cambios en la rama `master` se desplieguen automáticamente.

    ```bash
    az webapp deployment source config --name $APP_SERVICE_NAME --resource-group $RG_NAME --repository-type Github --repo-url $GH_REPO_URL --branch $GH_BRANCH
    ```

8.  **Verificar el Estado del Despliegue:**
    Puedes monitorear el progreso del despliegue en el Portal de Azure, o esperando unos minutos y luego intentando acceder a la URL de tu aplicación.

    ```bash
    az webapp show --resource-group $RG_NAME --name $APP_SERVICE_NAME --query "defaultHostName" --output tsv
    ```
    Copia la URL y pégala en tu navegador.

---

¡Tu aplicación debería estar desplegada y accesible en la URL proporcionada!
