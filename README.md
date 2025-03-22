Execute command `.venv\Scripts\activate` to start the enviorement

# PayESI - Backend

This project is a Flask-based web service, which provides APIs for user management, authentication, and other services. Below are the instructions on how to set up the project and run the web service.

## Prerequisites

Ensure you have the following installed:

- Python 3.8+ (recommended version)
- pip (Python package installer)
- Git (for version control)

## Setting Up the Virtual Environment

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. Create a virtual environment:

   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment:

   - On Windows:

     ```bash
     .\.venv\Scriptsctivate
     ```

   - On macOS/Linux:

     ```bash
     source .venv/bin/activate
     ```

4. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   If `requirements.txt` doesn't exist, you can manually install the necessary dependencies (like Flask, SQLAlchemy, etc.) using pip.

## Setting Up Environment Variables

Before running the web service, you need to create an `.env` file in the root of the project directory to store environment-specific variables.

1. Create an `.env` file in the root directory of the project with the following content (replace values with your own secrets):

   ```plaintext
   SECRET_KEY=your-secret-key
   JWT_EXPIRATION_DAYS=3600
   CREATE_DB_ON_STARTUP=True
   ```

2. Make sure to load the environment variables by adding this to your `app.py`:

   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

## Running the Web Service

1. Once the virtual environment is set up and dependencies are installed, you can run the web service with the following command:

   ```bash
   python app.py
   ```

   By default, the Flask web service will run on `http://127.0.0.1:5000/`.

2. If you want to run the service with a custom host and port, you can use:

   ```bash
   python app.py runserver --host=0.0.0.0 --port=8080
   ```

   This will make the service accessible on all network interfaces at port 8080.

## Database Setup

If you want the application to automatically create the database at startup, make sure the `CREATE_DB_ON_STARTUP` variable is set to `True` in your `.env` file.

The application will automatically create the necessary tables when the server starts if this is enabled.

## Testing the API

Once the service is up and running, you can use tools like [Postman](https://www.postman.com/) or `curl` to test the available API endpoints. For example, you can access `http://127.0.0.1:5000/users` to interact with the user-related API endpoints.

## Conclusion

You now have your environment set up and the Flask web service running. You can start developing and testing the application by interacting with the exposed APIs.

If you encounter any issues, please check the project documentation or feel free to raise an issue in the repository.
