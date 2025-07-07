# Image Server App

An image server built with FastAPI. It allows image uploads, displays uploaded images in the browser, and serves static files.

## Features

- Upload images through a simple web interface
- Display uploaded images in a gallery view
- Serve individual image files directly via URL
- Logging of all actions in a readable format
- Error handling for invalid file types
- Automatic favicon handling

## Requirements

\requirements.txt

Install dependencies:

```bash
pip install -r requirements.txt
```

## Project Structure
My_2nd_javarush_project/
│
├── app.py                  # Main FastAPI application
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

### 1. Build and start the services
```bash
docker compose up --build 
```
This will:

-Build the FastAPI app container
-Start both the app and Nginx
- Expose the app at http://localhost:8080

### 2. Configuration overview
| Service | Role          | Port            | Description                       |
| ------- | ------------- | --------------- | --------------------------------- |
| app     | FastAPI app   | 8000 (internal) | Serves the backend API            |
| nginx   | Reverse proxy | 80 (host)       | Forwards to app and serves static |

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