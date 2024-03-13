# Nyaya Dictionary Backend

## Overview

The Nyaya Dictionary is a Sanskrit-English dictionary developed by the Samskriti Foundation, Mysore.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/Raghav1909/nyaya-dictionary-backend.git
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

1. Navigate to the app directory within the project:
```bash
cd app
```

2. Start the server using Uvicorn:
```bash
uvicorn main:app --reload
```

## API Documentation

The API documentation can be accessed at: `http://localhost:8000/docs`
