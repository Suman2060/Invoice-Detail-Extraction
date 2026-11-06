# Invoice Data Extraction

An AI-powered invoice processing tool built with Python and Google Gemini. It analyzes invoice images and extracts key information, including invoice numbers, dates, supplier details, line items, quantities, prices, taxes, and totals. The extracted data is validated with Pydantic and returned in a clean, structured JSON format.

## Features

- Supports PNG, JPEG, and WEBP invoice images.
- Rejects missing, unsupported, or oversized images.
- Limits image size to 10 MB.
- Extracts invoice metadata, line items, and totals.
- Returns a predictable JSON response with an error message when processing fails.

## Requirements

- Python 3.9 or newer
- A Google Gemini API key

## Setup

1. Create and activate a virtual environment:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. Install the dependencies:

   ```powershell
   python -m pip install google-genai python-dotenv pydantic
   ```

3. Create a `.env` file in the project root:

   ```dotenv
   GEMINI_API_KEY=your_api_key_here
   GEMINI_MODEL=gemini-3-flash-preview
   ```

   `GEMINI_MODEL` is optional. If it is omitted, the script uses its built-in default model.

## Usage

The script currently reads the image at `samples/invoice.png`. Place the invoice image at that path and run:

```powershell
python extract_invoice.py
```

To process another image, either replace `samples/invoice.png` or update the path in `main()` in `extract_invoice.py`.

## Output

Successful extraction prints an object with this shape:

```json
{
  "success": true,
  "invoice": {
    "invoice_number": "INV-001",
    "invoice_date": "2024-10-14",
    "supplier_name": "Example Supplier",
    "currency": "USD",
    "items": [
      {
        "description": "Product",
        "quantity": 2,
        "unit": "pcs",
        "unit_price": 10.0,
        "line_total": 20.0
      }
    ],
    "subtotal": 20.0,
    "vat_amount": 3.0,
    "total_amount": 23.0
  }
}
```

Unreadable or missing values are returned as `null`. Extraction failures are printed as:

```json
{
  "success": false,
  "error": "Description of the failure"
}
```

The program exits with status code `1` when an error occurs.

## Project structure

```text
.
├── extract_invoice.py   # Invoice extraction logic and command-line entry point
├── samples/
│   └── invoice.png      # Input image used by the script
└── expected.json        # Example/reference invoice data
```

## Notes

- The API key must remain in `.env` and should never be committed.
- Invoice images are sent to the configured Gemini model for processing.
- The model is instructed not to guess missing values and to format dates as `YYYY-MM-DD`.
