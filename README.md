# News Search App

This project consists of a backend API and a frontend Streamlit application for searching and analyzing news articles.

## Project Structure
.
├── backend/
│ ├── api.py
│ ├── main.py
│ ├── utils.py
│ ├── requirements.txt
│ └── script.sh
└── frontend/
├── main.py
└── script.sh

## Backend

The backend is a Flask application that provides an API for searching and processing news articles.

### Files
- `main.py`: Sets up the Flask application and defines the API endpoint.
- `api.py`: Contains the main processing logic for search queries.
- `utils.py`: Contains utility functions for web scraping, sentiment analysis, topic extraction, and more.
- `requirements.txt`: Lists all Python dependencies for the backend.
- `script.sh`: Shell script for setting up and running the backend.

### Key Features
- Web scraping from non-js news websites
- Article summarization
- Sentiment analysis
- Topic extraction
- Comparative analysis of articles
- Text-to-speech conversion (Hindi)

### Setup and Running

1. Navigate to the backend directory
```
cd backend
```
2. Run the setup script
```
./script.sh
```
This script will:
- Create a virtual environment (if it doesn't exist).
- Activate the virtual environment.
- Install all the dependencies using requirement.txt.
- Run the Flask application using waitress.

The backend will start running on `http://127.0.0.1:8000`.

## Frontend

The frontend is a Streamlit application that provides a user interface for searching news and displaying the results.

### Files

- `main.py`: Contains the Streamlit application code.
- `script.sh`: Shell script for setting up and running the frontend.

### Key Features

- Search interface for news articles.
- Display of article summaries, topics, and sentiment.
- Comparative sentiment analysis visualization.
- Topic overlap analysis.
- Hindi audio playback of the final sentiment analysis.

### Setup and Running

1. Navigate to the frontend directory.
```
cd frontend
```
2. Run the setup script:
```
./script.sh
```
This script will:
- Create a virtual environment (if it doesn't exist)
- Activate the virtual environment
- Install Streamlit
- Run the Streamlit application

The frontend will be accessible in your web browser.

## Usage

1. Start the backend server.
2. Run the frontend Streamlit application.
3. Enter a search query in the frontend interface.
4. View the analyzed results, including article summaries, sentiment analysis, and topic analysis.
5. Listen to the Hindi audio summary of the final sentiment analysis.

## Dependencies

See `backend/requirements.txt` for a full list of Python dependencies.

## Note

Ensure that you have Python 3 and pip installed on your system before running the application.