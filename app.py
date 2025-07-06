import logging
import os
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from pathlib import Path
from dotenv import load_dotenv
from utils.file_utils import get_unique_name, file_validation


app = FastAPI()

load_dotenv()  # Load variables from .env
TEMPLATES_PATH = os.getenv('TEMPLATES_PATH')
IMAGES_PATH = os.getenv('IMAGES_PATH')
ALLOWED_EXTENSIONS = [ext.strip() for ext in os.getenv("ALLOWED_EXTENSIONS", "").split(",") if ext]


templates = Jinja2Templates(directory=TEMPLATES_PATH)

# Mount static files (assets, css,etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")


log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "app.log"

# Logging-Configuration
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Render the homepage of the image hosting service.
    This route handles GET requests to the root URL ("/") and returns the main landing page,
    which introduces the service and provides navigation to other features such as image upload
    and viewing uploaded images.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/upload/", response_class=HTMLResponse)
async def upload_image(request: Request):
    """
    Render the image upload page.
    This route handles GET requests to "/upload/" and displays the upload form
    where users can select and submit an image file to be stored.
    :param request:
    :return:
    """
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/upload/")
async def upload_img(request:Request, file:UploadFile = File(...)):
    """
    Handle image file upload via POST request.
    Receives an image file from the client, validates its extension and size,
    generates a unique filename, and saves the file locally in the configured image directory.

    """
    file_name = Path(file.filename)
    logging.info(f"File received: {file_name}")
    try:
        content = await file_validation(file, ALLOWED_EXTENSIONS)
    except HTTPException as e:
        logging.error(f"Upload failed for {file_name}: {e.detail}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "message": e.detail
            },
            status_code=e.status_code
        )

    new_file_name = get_unique_name(file_name)

    print(new_file_name)

    image_dir = Path(IMAGES_PATH)
    image_dir.mkdir(exist_ok=True)
    save_path = image_dir / new_file_name
    save_path.write_bytes(content)
    logging.info(f"File saved as: {save_path}")
    return {'message': f'File {file.filename} received. Saved as {save_path}'}


@app.get("/images/", response_class=HTMLResponse)
async def list_uploaded_images(request: Request):
    """
    Display a list of uploaded images.

    This route handles GET requests to "/images/" and renders an HTML page
    that lists all uploaded image files as clickable links. If no images exist,
    it displays an empty list.
    """
    image_dir = Path(IMAGES_PATH)
    if not image_dir.exists():
        return templates.TemplateResponse("images.html", {"request": request, "images": []})

    images = [f.name for f in image_dir.iterdir() if f.is_file()]
    return templates.TemplateResponse("images.html", {"request": request, "images": images})


@app.get("/images/{file_name}")
async def serve_image(file_name: str):
    """
    Serve an uploaded image directly in the browser.
    """
    file_path = Path(IMAGES_PATH) / file_name
    if not file_path.exists():
        logging.warning(f"Image not found: {file_name}")
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(file_path, media_type="image/jpeg")


if __name__== "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
