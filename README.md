# Nyaya Dictionary Backend

## Overview

Nyaya Khosha is a Sanskrit-English dictionary developed by Samskriti Foundation, Mysore.

### Links to Related Repositories:

- Nyaya Khosha frontend: [https://github.com/Samskriti-Foundation/nyaya-dictionary-frontend-main](https://github.com/Samskriti-Foundation/nyaya-dictionary-frontend-main)

- Nyaya Admin Panel frontend: [https://github.com/Samskriti-Foundation/nyaya-dictionary-frontend-admin](https://github.com/Samskriti-Foundation/nyaya-dictionary-frontend-admin)

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/Samskriti-Foundation/nyaya-dictionary-backend.git
   ```

2. **Install Dependencies:**
   
   **Option 1: Using pipenv**
   
   a. Install pipenv if not already installed:
   ```bash
   pip install pipenv
   ```
   b. Create a virtual environment and install dependencies:
  
   ```bash
   cd nyaya-dictionary-backend  # Navigate to the project directory
   pipenv install
   ```

   **Option 2: Using a Virtual Environment**

   a. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
   
   b. Activate the virtual environment:
     - **Linux/macOS:**
       ```bash
       source venv/bin/activate
       ```
     - **Windows:**
       ```bash
       venv\Scripts\activate
       ```
   c. Install the required dependencies:
      ```bash
      pip install -r requirements.txt
      ```


## Run the backend server

1. Start the server using Uvicorn:
```bash
uvicorn app.main:app --reload
```

## Run tests

1. Run tests with Pytest:
```bash
pytest -v
```

## API Documentation

The API documentation can be accessed at: `http://localhost:8000/docs`
