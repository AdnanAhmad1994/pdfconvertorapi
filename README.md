# PDF Converter API

A scalable, secure API for converting PDF files into DOCX, JPEG, PPT, and HTML formats using Python.

## Features

- Convert PDFs to multiple formats (DOCX, JPEG, PPT, HTML)
- Support for batch processing and asynchronous workflows
- Ensures layout fidelity and accurate text/image extraction
- Secure implementation with API key authentication
- Persistent storage of conversion tasks using SQLite
- Clean and intuitive web interface for testing
- Scalable architecture using Docker containerization

## Demo

The API provides a web interface for testing at http://localhost:8000/ui.

## Getting Started

### Prerequisites

- Python 3.8+ (developed with Python 3.13.2)
- Poppler (for pdf2image/JPEG conversion)
  - **Windows**: Download from [poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases/)
  - **Linux**: `sudo apt-get install poppler-utils`
  - **macOS**: `brew install poppler`

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/AdnanAhmad1994/pdfconvertorapi.git
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

### Docker Deployment

1. Build and start the containers:
   ```
   docker-compose up -d
   ```

2. The API will be available at http://localhost:8000

## API Endpoints

### Conversion

- `POST /api/v1/conversion/`: Start a new conversion
- `GET /api/v1/conversion/{task_id}`: Get conversion status
- `GET /api/v1/conversion/{task_id}/download`: Download the converted file
- `DELETE /api/v1/conversion/{task_id}`: Cancel a conversion
- `GET /api/v1/conversion`: Get supported formats
- `POST /api/v1/conversion/validate`: Validate a PDF file

### Authentication

In production mode, API key authentication is required for all endpoints.

## Project Structure

```
pdfconvertorapi/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── api/                    # API endpoints
│   ├── core/                   # Application settings
│   ├── db/                     # Database operations
│   ├── models/                 # Pydantic models
│   ├── security/               # Authentication
│   ├── services/               # PDF conversion services
│   └── utils/                  # Utility functions
├── static/                     # Static assets for frontend
├── templates/                  # HTML templates
├── docker/                     # Docker configuration
├── requirements.txt            # Project dependencies
└── README.md                   # This file
```

## Development

### Adding New Conversion Formats

1. Create a new service in `app/services/conversions/`
2. Update the `ConversionFormat` enum in `app/models/conversion.py`
3. Add the format to the supported formats list in `app/api/endpoints/conversion.py`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - The web framework used
- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF processing library
- [pdf2docx](https://github.com/dothinking/pdf2docx) - PDF to DOCX conversion
