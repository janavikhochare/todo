## Todo App

## Docker commands
```
    Commands to run via Docker
    docker build -t my_flask_app .
    docker run -p 5000:5000 my_flask_app
```


# To-Do API

This is a simple Flask RESTful API for managing to-do tasks.s

## Installation

1. Clone this repository:

   ```
   git clone https://github.com/janavikhochare/todo.git
   ```

2. Install the required Python packages:

   ```
   pip install -r requirements.txt
   ```

3. Create a SQLite database by runing this file in python:

   ```
   python database.py
   ```

4. Run the Flask server:

   ```
   python api.py
   ```

## Usage

### Users

#### Register a new user

```
POST /users/

Parameters:
- email (string): User email
- password (string): User password
- first_name (string): User first name
- last_name (string): User last name

Response:
- 201 Created: User registered successfully
- 409 Conflict: User already exists
```

#### Get user details by ID

```
GET /users/<user_id>/?access_token=<access_token>

Parameters:
- user_id (integer): User ID
- access_token (string): Access token

Response:
- 200 OK: User details
```

### Tasks

#### Add a new task

```
POST /tasks/

Parameters:
- user_id (integer): User ID
- access_token (string): Access token
- task (string): Task description
- priority (string): Task priority
- status (string): Task status

Response:
- 201 Created: Task added successfully
```

#### Update a task

```
PUT /tasks/<task_id>/

Parameters:
- user_id (integer): User ID
- access_token (string): Access token
- task_id (string): Task ID
- task (string): Task description
- priority (string): Task priority
- status (string): Task status

Response:
- 200 OK: Task updated successfully
```

#### Delete a task

```
DELETE /tasks/<task_id>/

Parameters:
- user_id (integer): User ID
- access_token (string): Access token
- task_id (string): Task ID

Response:
- 204 No Content: Task deleted successfully
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.






