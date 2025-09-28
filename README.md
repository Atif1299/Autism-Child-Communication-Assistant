# Autism Child Communication Assistant

This is a full-stack application designed to assist children with autism in communication. It features an intelligent agent backend powered by LangGraph and a user-friendly React frontend.

## Features

- **Sentence Completion:** Helps complete fragmented sentences into coherent thoughts.
- **Conversational Agent:** Provides context-aware, supportive responses.
- **Database Integration:** Stores child profiles and conversation history in a PostgreSQL database.
- **Text-to-Speech:** Reads agent responses aloud with a choice of voices.
- **Speech-to-Text:** Allows for voice input for sentence completion.

---

## Project Setup: End-to-End Instructions

Follow these steps carefully to get the entire application running locally.

### Step 1: Clone the Repository

First, clone the project to your local machine.

```bash
git clone https://github.com/Atif1299/Autism-Child-Communication-Assistant.git
cd Autism-Child-Communication-Assistant
```

### Step 2: Set Up the PostgreSQL Database

This application requires a PostgreSQL database.

1.  **Install PostgreSQL:** If you don't have it, download and install it from the [official website](https://www.postgresql.org/download/). During installation, you will be asked to set a password for the superuser (`postgres`). **Remember this password.**

2.  **Create the Database and User:**
    *   Open the **SQL Shell (psql)**.
    *   Log in as the `postgres` superuser (use the password you just set).
    *   Run the following SQL commands one by one:

    ```sql
    -- Create a new database for the application
    CREATE DATABASE autism_communication_db;

    -- Create a dedicated user for the application
    CREATE USER comm_user WITH PASSWORD 'your_strong_password'; -- Replace with a secure password

    -- Grant all privileges on the new database to the new user
    GRANT ALL PRIVILEGES ON DATABASE autism_communication_db TO comm_user;
    ```

3.  **Grant Schema Privileges:**
    *   Connect to your new database by typing: `\c autism_communication_db`
    *   Run the final grant command:
    ```sql
    GRANT ALL ON SCHEMA public TO comm_user;
    ```
    *   You can now exit `psql` by typing `\q`.

### Step 3: Configure the Backend

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create a Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    *   Create a copy of the `.env.example` file and name it `.env`.
    *   Open the new `.env` file and fill in your details:
        *   **`DATABASE_URL`**: Use the details from Step 2. The format is `postgresql://USER:PASSWORD@HOST:PORT/DATABASE_NAME`. For example: `postgresql://comm_user:your_strong_password@localhost:5432/autism_communication_db`
        *   **`OPENAI_API_KEY`**: Enter your secret API key from OpenAI.

### Step 4: Run the Backend Server

With the configuration complete, you can now run the backend.

```bash
uvicorn app.main:app --reload
```

The server should start on `http://127.0.0.1:8000`. The first time it runs, it will automatically create the necessary tables in your database.

**Keep this terminal running.**

### Step 5: Set Up and Run the Frontend

1.  **Open a new, separate terminal.**

2.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

3.  **Install Dependencies:**
    ```bash
    npm install
    ```

4.  **Run the Frontend Application:**
    ```bash
    npm start
    ```

This will open the application in your browser at `http://localhost:3000`. It is already configured to connect to your backend.

You are now ready to use the application!
