#!/bin/bash

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing packages..."
pip install streamlit


echo "Running streamlit..."
streamlit run main.py



