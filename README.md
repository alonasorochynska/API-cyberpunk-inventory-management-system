# FastAPI Cyberpunk Inventory Management System

A simple inventory management system for a cyberpunk-themed game using FastAPI, SQLAlchemy, PostgreSQL, 
and Pydantic models. The system manages items belonging to their categories that players can acquire in the game. 
The API provides basic CRUD (Create, Read, Update, Delete) functionality for these items.

It implements robust authentication and authorization to control access to the API. Only authenticated 
users are allowed to perform CRUD operations, including adding items to and removing items from their inventory. 
However, reading items remains accessible to all users.

It includes Swagger and Redoc documentation, along with docstrings for all functions, and examples in schemas. 
Pytests are implemented for all custom functions. 

The FastAPI application is dockerized for easy deployment using Docker Compose.

## Getting Started

To run application using Docker follow these steps:

### 1. Clone the repository and navigate to the directory:

```shell
git clone https://github.com/alonasorochynska/API-cyberpunk-inventory-management-system.git
cd API-cyberpunk-inventory-management-system
```

### 2. Set environment variables:

Copy the `.env.sample` file and rename it to `.env`. Open the `.env` file and specify the necessary values 
for the variables:

* `DATABASE_URL`: URL to connect to the database. By default, it is configured to work with the PostgreSQL 
container in Docker. If you plan to run the application locally, uncomment the line containing `localhost` 
and comment out the one with `db`.

* `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`: These values are used to configure the PostgreSQL 
database in Docker. If you are using Docker Compose, leave them as is.

* `SECRET_KEY`: Replace your_secret_key with a randomly generated key for encrypting tokens (any 
random character set can be used).

* `ALGORITHM`: The algorithm used for JWT tokens. Leave `HS256` unless you need to change it.

* `ACCESS_TOKEN_EXPIRE_MINUTES`: Access token expiration time (in minutes). By default, it is 30 minutes, 
but you can change the value to your liking.


### 3. Build and run the container:

```shell
docker-compose up --build
```
After building, you can access the application in your browser at: `http://127.0.0.1:8000/`.

## Try it out!

### 1. Start using:

* Refer to `http://127.0.0.1:8000/docs/` page.

### 2. Register User and login:

* Choose user section and press `POST (/register)` button to register a user.
* Select `POST (/token)` and enter your `username` and `password` to obtain a token.
* Copy the access token and use it for authorization in tools like Postman or ModHeader. For example, 
include `Bearer <access_token>` in the Authorization header.
* Check result on `GET (/users/me)`.

**_Note_**: Before any action press `Try it out`, input data and choose `execute`.

### 3. Explore Category section:

* Choose `POST (/categories/)` to create one for future usage in Items.
* Inspect `GET (/categories/)` to see what was created.
* Delete category using `DELETE (/categories/{category_id})` button.

**_Note_**: Only registered users can create or delete categories.

### 4. Explore Item section:

* Choose `POST (/items/)` to create an Item.
* Use `PUT (/items/{item_id})` to update a description of Item.
* Delete an item using `DELETE (/items/{item_id})` button.
* Check details by `GET (/items/{item_id})` opportunity.
* Inspect `GET (/items/)` to see all existing items.

**_Note_**: Unregistered users can only see existing items.<br>
**_Note_**: To create an item, you must choose an existing category.

### 5. Explore Inventory section:

* Choose `POST (/inventory/add/{item_id})` to add an item to users inventory.
* Press `DELETE (/inventory/remove/{item_id})` to remove an item from users inventory.

**_Note_**: Visit `/users/me` page to check your current inventory

### 6. Check out pagination:

* Go to `/categories/?page=2` to view the second page of categories if more than 5 categories exist.
* Visit `/items/?page=2` if there are more than 5 items.

## Testing

**_Note_**: Currently, testing is not connected to Docker, so to run tests, you need to execute them on your 
local machine.

### 1. Create and activate a virtual environment:

```shell
# macOS/Linux
python3 -m venv venv
source venv/bin/activate
# Windows
python -m venv venv
venv\Scripts\activate
```

### 2. Install the required packages:

```shell
pip install -r requirements.txt
```

### 3. Configure the environment variable

In the `.env file`, change the `DATABASE_URL` to use `localhost` instead of `db`. Example:

```shell
DATABASE_URL=postgresql://username:password@localhost:5432/cyberpunk
```

### 4. Apply database migrations:

Before running tests, ensure that your database is up to date by running the migrations:

```shell
alembic upgrade head
```

### 5. Run the tests:

```shell
pytest
```

### 6. To run the application locally:

If you want to run the application locally, use the following command:

```shell
python -m uvicorn main:app --reload 
```

### Important note regarding testing and libraries
_We are actively working on improving the testing process and fully integrating it with Docker. Additionally, 
some libraries used in the project (such as Pydantic and Passlib) have deprecated functions that will need to be 
updated. We plan to address these issues and update the libraries in future releases to ensure compatibility with 
newer versions. Until then, you may see warnings related to deprecated methods, but they do not affect the 
functionality of the application at this time._

<hr>

Thank you for exploring this project! We're working on improving features and updating libraries. Contributions 
and feedback are welcome - feel free to open an issue on GitHub.