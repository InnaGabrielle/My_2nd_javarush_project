from datetime import datetime  # <— wichtig: Klassenimport!
import logging
import os
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from pathlib import Path
from dotenv import load_dotenv
from utils.file_utils import get_unique_name, file_validation
from db import connect_db, close_db, create_table_db, save_image, get_all_images, delete_image
from contextlib import asynccontextmanager

load_dotenv()


TEMPLATES_PATH = os.getenv('TEMPLATES_PATH', 'templates')
IMAGES_PATH = os.getenv('IMAGES_PATH', 'images')
ALLOWED_EXTENSIONS = [ext.strip() for ext in os.getenv("ALLOWED_EXTENSIONS", "jpg,jpeg,png,gif").split(",") if ext]


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting up...")
    create_table_db()
    yield
    logging.info("Shutting down...")

app = FastAPI(lifespan=lifespan)

# Templates & Static mount
templates = Jinja2Templates(directory=TEMPLATES_PATH)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "app.log"
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler(log_file, encoding="utf-8"), logging.StreamHandler()]
)

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.ico")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/upload/", response_class=HTMLResponse)
async def upload_image(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.get("/delete/{filename}", response_class=HTMLResponse)
async def delete_image_view(request: Request, filename: str):
    """
    FastAPI route to delete an image record by filename
    :param request: the incoming HTTP request
    :param filename: the filename to delete from the DB
    :return: TemplateResponse: rendered html template after deletion
    """
    # Delete DB Record
    delete_image(filename)

    # Delete from filesystem
    file_path = os.path.join(IMAGES_PATH, filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            logging.info(f"[FS] File {file_path} has been deleted.")
        except Exception as e:
            logging.error(f"[FS] Error deleting file {file_path}: {e}")
    return RedirectResponse(url="/images-list/", status_code=303)


@app.post("/upload/")
async def upload_img(request: Request, file: UploadFile = File(...)):
    file_name = Path(file.filename)
    logging.info(f"File received: {file_name}")

    # 1) Validation
    try:
        content = await file_validation(file, ALLOWED_EXTENSIONS)
    except HTTPException as e:
        logging.error(f"Upload failed for {file_name}: {e.detail}")
        return templates.TemplateResponse("error.html", {"request": request, "message": e.detail}, status_code=e.status_code)

    # 2) Save
    new_file_name = get_unique_name(file_name)
    image_dir = Path(IMAGES_PATH)
    image_dir.mkdir(exist_ok=True)
    save_path = image_dir / new_file_name
    save_path.write_bytes(content)
    logging.info(f"File saved as: {save_path}")

    # 3) Metadata
    size = save_path.stat().st_size
    file_type = file.content_type or "unknown"
    upload_time = datetime.now()

    # 4) DB-Insert
    try:
        save_image(
            filename=new_file_name,
            original_name=file_name.name,
            size=size,
            file_type=file_type,
            upload_time=upload_time
        )
        logging.info(f"Metadata for {new_file_name} stored in DB")
    except Exception as e:
        logging.error(f"DB insert failed for {new_file_name}: {e}")
        raise HTTPException(status_code=500, detail="Database insert failed")

    return templates.TemplateResponse(
        "upload.html",
        {
            "request": request,
            "message": f"File {file.filename} successfully uploaded."
        }
    )


@app.get("/images-list/", response_class=HTMLResponse)
async def list_uploaded_images(request: Request):
    images = get_all_images()
    return templates.TemplateResponse("images.html", {"request": request, "images": images})

@app.get("/images/{file_name}")
async def serve_image(file_name: str):
    file_path = Path(IMAGES_PATH) / file_name
    if not file_path.exists():
        logging.warning(f"Image not found: {file_name}")
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path, media_type="image/jpeg")

@app.get("/db-test")
async def db_test_connect():
    conn = connect_db()
    if conn:
        close_db(conn)
        return {'status': 'ok', 'message': 'Connection to database successful'}
    else:
        return {'status': 'error', 'message': 'Connection to database failed'}

if __name__== "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000)  # host 0.0.0.0 for Container
