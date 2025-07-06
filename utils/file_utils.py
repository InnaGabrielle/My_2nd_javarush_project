from pathlib import Path
import uuid
from fastapi import HTTPException, UploadFile


def is_allowed_file(filename: Path, allowed_extensions: list) -> bool:
    """
    Checks whether the given file extension is allowed
    Parameters:
        filename (Path):
        allowed_extensions (list)
    Returns:
        bool:
    """
    #extension = filename.split(".")[-1].lower()
    extension = filename.suffix.lower()
    return extension in allowed_extensions


def get_unique_name(filename: Path) -> str:
    """
    Generates and returns unique name of the input file

    Parameters:
        filename (Path):
    Returns:
        String: unique name of the file
    """
    extension = filename.suffix.lower()
    unique_name = f"{uuid.uuid4().hex}{extension}"
    print(f"{unique_name=}")
    return unique_name


async def file_validation(file: UploadFile, allowed_extensions: list, max_file_size =  5 * 1024 * 1024) -> bytes:
    """
    Validates an uploaded file by checking its extension and size.

    Parameters:
        file (UploadFile): The uploaded file to validate.
        allowed_extensions (list): A list of allowed file extensions).
        max_file_size (int): Maximum allowed file size in bytes. Defaults to MAX_FILE_SIZE.

    Raises:
        HTTPException: If the file extension is not allowed or the file exceeds the max size.

    Returns:
        bytes: The raw content of the file.
    """
    file_name = Path(file.filename)
    if not is_allowed_file(file_name, allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file extension for '{file.filename}'. "
                   f"Allowed extensions: {', '.join(allowed_extensions)}"
        )
    else:
        print("Valid extension")
    content = await file.read(max_file_size + 1)
    if len(content) > max_file_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large – limit is {max_file_size // (1024 * 1024)} MB"
        )
    else:
        print("Valid file size")

    file.file.seek(0)
    return content

