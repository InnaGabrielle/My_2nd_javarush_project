# Image Server App

An image server built with FastAPI. It allows image uploads, displays uploaded images in the browser, and serves static files.

## Features

- Upload images through a simple web interface
- Display uploaded images in a gallery view
- Serve individual image files directly via URL
- Logging of all actions in a readable format
- Error handling for invalid file types
- Automatic favicon handling
- Image metadata is stored in a PostgreSQL database 
- Paginated gallery view (10 images per page) with navigation buttons 
- Delete functionality (removes both database record and physical file)
- Database administration with pgAdmin included in Docker Compose

## Requirements

\requirements.txt

Install dependencies:

```bash
pip install -r requirements.txt
```
## Database setup
You need a running PostgreSQL instance. Configure connection details via environment variables:

DB_NAME
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT

Run the following once to create the images table:

```bash
python -c "from app import create_table_db; create_table_db()"
```

## Project Structure
My_2nd_javarush_project/
│
├── app.py                  # Main FastAPI application
├── db.py                   # Database helper functions
├── templates/              # HTML templates
├── static/                 # Static files (e.g. favicon.ico, styles.css)
├── images/                 # Directory for uploaded images
├── utils/                  # Directory for helper functions
├── logs/
│   └── app.log             # Log file for events and errors
└── README.md               # Project documentation

## Running the App locally
Start the development server with:
```bash
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```
The server will be available at: http://localhost:8000

## Running with Docker
To run the application inside a Docker container:

### 1. Build the image
```bash
docker build -t image-server-app .
```
### 2. Run the container
```bash
docker run -it -p 8000:8000 image-server-app  
```
This starts the app at http://localhost:8000

## Running with Docker Compose
The project includes a `docker-compose.yml` file with two services:

- `app`: The FastAPI image server
- `nginx`: A reverse proxy that forwards requests to the app
- `db`: PostgreSQL database for image metadata
- `pgadmin`: Web UI for managing the database

### 1. Build and start the services
```bash
docker compose up --build 
```
This will:

- Build the FastAPI app container
- Start the PostgreSQL database and pgAdmin
- Start both the app and Nginx
- Expose the app at http://localhost:8080

### 2. Configuration overview
| Service | Role             | Port            | Description                       |
|---------|------------------|-----------------| --------------------------------- |
| app     | FastAPI app      | 8000 (internal) | Serves the backend API            |
| nginx   | Reverse proxy    | 80 (host)       | Forwards to app and serves static |
| db      | PostgreSQL DB    | 5432 (internal) | Stores image metadata such as filename, original name, size, type, timestamp |
| pgadmin | DB management UI | 5050 (host)     | Web interface for managing the PostgreSQL database (tables, queries, users) |

### 3.Stopping the services
```bash
docker compose down
```
## Logging
All actions (uploads, errors, etc.) are logged in a readable format like:
```yaml
[2025-07-07 13:45:10] Upload: image.jpg saved successfully.
[2025-07-07 13:46:22] Error: Invalid file type.
```
The log file is located at: logs/app.log