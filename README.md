# Tafilapi HTML Extractor & Cleaner

A modern, REST API to extract and clean HTML content. It includes support for standard network fetching, stealthy browser-based scraping with cloakbrowser, customizable cleanup levels.

---

## Features

- **Text & Metadata Extraction**: Extract clean content (plain text, markdown, HTML, XML, etc.) or document metadata using [Trafilatura](https://github.com/adbar/trafilatura).
- **Stealth Browser Scraping**: Supports rendering JavaScript-heavy or protected pages using `CloakBrowser` (powered by Cloakbrowser/Playwright).
- **HTML Sanitization**: Clean, reformat, and normalize HTML content using [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) across 5 levels of strictness.
- **Bearer Token Security**: Restricts access to endpoints using a customizable API security token.
- **Self-Testing Health Checks**: Includes a robust health check that runs self-tests of the extraction pipeline.
- **Docker-Ready**: Prepared for containerization.

---

## Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **ASGI Server**: [Uvicorn](https://www.uvicorn.org/)
- **Package Manager**: [uv](https://github.com/astral-sh/uv) (Fast Python packaging tool)
- **Extraction Engine**: [Trafilatura](https://trafilatura.readthedocs.io/)
- **HTML Cleanup**: [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) (lxml parser)
- **Stealth Fetching**: [CloakBrowser](https://github.com/cloakbrowser/cloakbrowser)

---

## Directory Structure

```text
tafilapi/
├── app/
│   ├── api/
│   │   ├── routes/         # Endpoint routers: health, extraction, clean
│   │   └── dependencies.py # Authentication and dependencies
│   ├── core/
│   │   └── config.py       # Configuration settings
│   ├── schemas/            # Pydantic request and response models
│   └── services/           # Extraction and cleaning logic, custom exceptions
├── tests/                  # Pytest test suite
├── Dockerfile              # Docker container setup
├── .dockerignore           # Excluded files from Docker context
├── pyproject.toml          # Project configuration and dependency specifications
├── uv.lock                 # uv dependency lock file
└── main.py                 # Application entrypoint
```

---

## Installation & Setup

Ensure you have Python 3.13+ installed.

### 1. Install `uv`
If you do not have `uv` installed, get it via:
```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Install Project Dependencies
Run the following command at the root of the project to create a virtual environment and install all packages:
```bash
uv sync
```

### 3. Set Up Environment Variables
Create a `.env` file in the root directory:
```env
API_AUTH_TOKEN="your-super-secret-token"
LOG_LEVEL="INFO"
CLOAKBROWSER_CDP_URL="http://localhost:9222"
```

---

## Running the Application

### Locally
Start the development server with live reload enabled:
```bash
uv run uvicorn main:app --reload --port 8000
```
Visit http://127.0.0.1:8000/docs to explore the interactive API documentation.

### Using Docker
1. **Build the image**:
   ```bash
   docker build -t tafilapi .
   ```
2. **Run the container**:
   ```bash
   docker run -p 8000:8000 -e API_AUTH_TOKEN="your-super-secret-token" tafilapi
   ```

---

## API Endpoints

All endpoints except `/health` require a `Authorization: Bearer <API_AUTH_TOKEN>` header.

### 1. Health Check
* **Endpoint**: `GET /health`
* **Description**: Performs a self-test of the extraction engine.
* **Response**:
  ```json
  {
    "status": "healthy",
    "message": "Application is working fine, extraction self-test succeeded."
  }
  ```

### 2. Extract HTML Content
* **Endpoint**: `POST /extract`
* **Description**: Extract main text/content or metadata from raw HTML or a URL.
* **Sample Request**:
  ```json
  {
    "url": "https://example.com",
    "output_format": "txt",
    "cloakbrowser": true
  }
  ```
* **Sample Response**:
  ```json
  {
    "success": true,
    "data": "Extracted main text content goes here...",
    "source": "url",
    "url": "https://example.com",
    "error": null
  }
  ```

### 3. Clean HTML Content
* **Endpoint**: `POST /clean`
* **Description**: Normalizes and cleans raw HTML or fetches and cleans HTML from a URL.
* **Clean Levels**:
  - `correct_only`: Only runs basic parser normalization.
  - `styled`: Retains text content, basic formatting, and styling elements.
  - `permissive`: Retains most tags (headings, lists, formatting, links).
  - `standard`: Retains structural/text content while stripping scripts, styles, forms, and tracking objects.
  - `minimal`: Retains structural blocks only, removing all layout styling, tables, and lists.
* **Sample Request**:
  ```json
  {
    "raw_html": "<div><p>Hello <span style='color:red;'>World</span></p></div>",
    "clean_level": "minimal"
  }
  ```
* **Sample Response**:
  ```json
  {
    "success": true,
    "data": "<html>\n <body>\n  <p>\n   Hello\n   World\n  </p>\n </body>\n</html>\n",
    "raw_html": null,
    "source": "raw_html",
    "url": null,
    "error": null
  }
  ```
---

## Running Tests

Execute the test suite using `pytest`:
```bash
uv run pytest
```