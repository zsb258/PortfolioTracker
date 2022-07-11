#! /bin/bash

if [ ! -d "venv" ]; then
    # create virtual environment named "venv"
    echo "Creating virtual environment..."
    python3 -m venv venv

    # activate virtual environment
    echo "Activating virtual environment..."
    source ./venv/bin/activate

    # install dependencies
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    # activate virtual environment
    echo "Activating virtual environment..."
    source ./venv/bin/activate
fi

# delete old database
echo "Deleting old database..."
rm -f db.sqlite3

# migrate database
echo "Applying database migrations..."
python3 manage.py migrate

# start django server
echo "Starting django server..."
python3 manage.py runserver