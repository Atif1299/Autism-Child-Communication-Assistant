# Supportive Communication Agent API

This project is a FastAPI-based backend for a supportive communication agent designed to assist children with autism.

## Project Structure

- **/app**: Contains the main application code.
  - **/api**: Defines the API endpoints.
  - **/core**: Holds configuration and core settings.
  - **/models**: Contains Pydantic models for data validation.
  - **/services**: Implements the core business logic.
- **requirements.txt**: Lists the Python dependencies for the project.
- **.gitignore**: Specifies files and directories to be ignored by Git.
- **README.md**: This file.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

To run the application, use `uvicorn`:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. You can access the interactive API documentation at `http://127.0.0.1:8000/docs`.
