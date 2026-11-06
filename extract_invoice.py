import json
import mimetypes
import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors
from google.genai import types
from pydantic import BaseModel

load_dotenv(override=True)

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
SUPPORTED_TYPES = {"image/png", "image/jpeg", "image/webp"}
MAX_IMAGE_BYTES = 10 * 1024 * 1024

PROMPT = (
    "Extract the data from this invoice. Rules: "
    "copy numbers exactly as printed, without thousands separators or currency symbols; "
    "use null for anything missing or unreadable, never guess; "
    "the supplier is the company issuing the invoice at the top, NOT the 'Bill To' customer; "
    "dates must be in YYYY-MM-DD format; "
    "split quantity into a number and a unit (for example 50 and 'pcs')."
)



class Item(BaseModel):
    description: Optional[str]
    quantity: Optional[float]
    unit: Optional[str]
    unit_price: Optional[float]
    line_total: Optional[float]


class Invoice(BaseModel):
    invoice_number: Optional[str]
    invoice_date: Optional[str]
    supplier_name: Optional[str]
    currency: Optional[str]
    items: list[Item]
    subtotal: Optional[float]
    vat_amount: Optional[float]
    total_amount: Optional[float]



def load_image(path):
    """Return (image_bytes, mime_type). Raise ValueError with a clear message on problems."""
    path = Path(path)

    if not path.is_file():
        raise ValueError(f"Image not found: {path}")

    mime_type = mimetypes.guess_type(path.name)[0]
    if mime_type not in SUPPORTED_TYPES:
        raise ValueError(
            f"Unsupported file type '{mime_type}'. Use PNG, JPG or WEBP."
        )

    if path.stat().st_size > MAX_IMAGE_BYTES:
        raise ValueError("Image is too large (max 10 MB).")

    return path.read_bytes(), mime_type



def extract_invoice_data(image_bytes, mime_type):
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY not found. Add it to your .env file.")

    client = genai.Client(api_key=key)

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                PROMPT,
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=Invoice,
            ),
        )
    except genai_errors.APIError as e:
        raise RuntimeError(f"AI request failed: {e}") from e

    if response.parsed is None:
        raise RuntimeError("The AI did not return data in the expected format.")

    return response.parsed.model_dump()  



def main():
    try:
        image_bytes, mime_type = load_image("samples/invoice.png")
        result = extract_invoice_data(image_bytes, mime_type)
    except (ValueError, RuntimeError) as e:
        print(json.dumps({"success": False, "error": str(e)}, indent=2))
        sys.exit(1)

    print(json.dumps({"success": True, "invoice": result}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
