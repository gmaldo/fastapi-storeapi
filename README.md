# 🛍️ FastAPI Store API

¡Bienvenido a la API de la tienda FastAPI! Este proyecto proporciona una API RESTful para gestionar productos.

## 🏛️ Arquitectura

Este proyecto sigue una arquitectura en capas para separar las responsabilidades y mejorar la mantenibilidad:

-   **`main.py`**: El punto de entrada de la aplicación FastAPI. Inicializa la aplicación y carga los routers.
-   **`controllers`**: La capa de presentación. Define los endpoints de la API, gestiona las solicitudes HTTP y las respuestas. No contiene lógica de negocio.
-   **`services`**: La capa de lógica de negocio. Orquesta las operaciones y contiene la lógica principal de la aplicación. Se comunica con la capa de repositorio.
-   **`repositories`**: La capa de acceso a datos. Es responsable de la comunicación directa con la base de datos (lectura y escritura). Abstrae la lógica de la base de datos del resto de la aplicación.
-   **`schemas`**: Contiene los modelos Pydantic. Se utilizan para la validación de datos, serialización y documentación automática de la API.
-   **`models`**: Define los modelos de la base de datos utilizando SQLAlchemy ORM.

## 🚀 Instalación

Sigue estos pasos para configurar el entorno de desarrollo:

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/gmaldo/fastapi-storeapi.git
    cd fastapi-storeapi
    ```

2.  **Crea un entorno virtual:**
    ```bash
    python -m venv venv
    ```

3.  **Activa el entorno virtual:**
    *   En macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
    *   En Windows:
        ```bash
        venv\Scripts\activate
        ```

4.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

## ▶️ Ejecutando la Aplicación

Para iniciar la aplicación, ejecuta el siguiente comando en la raíz del proyecto:

```bash
uvicorn app.main:app --reload
```

La API estará disponible en `http://127.0.0.1:8000`.

## 📡 Endpoints de la API

Aquí tienes una lista de los endpoints disponibles y cómo probarlos usando `curl`.

### 📦 Productos

#### 1. Obtener todos los productos
Recupera una lista de todos los productos en la base de datos.

*   **Método:** `GET`
*   **Endpoint:** `/products/`
*   **Comando `curl`:**
    ```bash
    curl -X GET http://127.0.0.1:8000/products/
    ```

#### 2. Obtener un producto por ID
Recupera un producto específico usando su ID.

*   **Método:** `GET`
*   **Endpoint:** `/products/{product_id}`
*   **Comando `curl` (ejemplo con ID 1):**
    ```bash
    curl -X GET http://127.0.0.1:8000/products/1
    ```

#### 3. Crear un nuevo producto
Añade un nuevo producto a la base de datos.

*   **Método:** `POST`
*   **Endpoint:** `/products/`
*   **Comando `curl`:**
    ```bash
    curl -X 'POST' \
      'http://127.0.0.1:8000/products/' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{ 
      "name": "Maceta",
      "price": 100,
      "description": "Un Macetero",
      "category": "Bazar",
      "stock": 2,
      "image": "image_string"
    }'
    ```

#### 4. Actualizar un producto
Actualiza los detalles de un producto existente por su ID.

*   **Método:** `PUT`
*   **Endpoint:** `/products/{product_id}`
*   **Comando `curl` (ejemplo con ID 1):**
    ```bash
    curl -X 'PUT' \
      'http://127.0.0.1:8000/products/1' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{ 
      "name": "Maceta de Lujo",
      "price": 150,
      "description": "Un Macetero premium",
      "category": "Bazar",
      "stock": 5,
      "image": "image_string"
    }'
    ```


#### 5. Eliminar un producto
Elimina un producto de la base de datos por su ID.

*   **Método:** `DELETE`
*   **Endpoint:** `/products/{product_id}`
*   **Comando `curl` (ejemplo con ID 1):**
    ```bash
    curl -X DELETE http://127.0.0.1:8000/products/1
    ```