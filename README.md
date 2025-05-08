# PDF Converter API

A scalable, secure API for converting PDF files into DOCX, JPEG, PPT, and HTML formats using Python.

## Features

- Convert PDFs to multiple formats (DOCX, JPEG, PPT, HTML)
- Support for batch processing and asynchronous workflows
- Ensures layout fidelity and accurate text/image extraction
- Secure implementation with HTTPS, rate-limiting, and input validation
- Scalable architecture using Docker containerization

## Getting Started

### Prerequisites

- Python 3.8+ (developed with Python 3.13.2)
- Poppler (for pdf2image)

### Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd pdfconvertorapi
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   
   # Windows
   venv\Scripts\activate.bat
   
   # Linux/macOS
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the API

Start the development server:

```
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

API documentation is automatically generated and available at:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## API Endpoints

*Coming soon as development progresses*

## Project Structure

```
pdf-converter-api/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   └── endpoints/          # API route definitions
│   ├── core/
│   │   └── config.py           # Application settings
│   ├── services/
│   │   └── conversions/        # PDF conversion services
│   ├── models/                 # Pydantic models
│   └── utils/                  # Utility functions
├── tests/                      # Test directory
├── requirements.txt            # Project dependencies
└── README.md                   # This file
```

## License

*Add appropriate license information*

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - The web framework used
- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF processing library
- [pdf2docx](https://github.com/dothinking/pdf2docx) - PDF to DOCX conversion
