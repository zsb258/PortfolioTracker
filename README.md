# Portfolio Tracker
Web application developed for Code To Connect 2022 – FICC Problem Statement

<br>

Recommended environment:
1. Python 3.8+
2. Node.js 16 LTS

### Starting the server application
1. Run

    ```console
    $ bash start.sh
    ```

2. Keep this terminal running to provide data for the client UI

### Starting the client UI
1. Run on a new terminal
    ```console
    $ bash client.sh
    ```

2. Open [localhost:3000](http://localhost:3000) in a browser to see the client interface

### Publishing events to the server to see changes
Runs a script to emulate sending market data or trade events to the server.
Action is done using scheduler that periodically makes POST requests to server.
1. Run on a new terminal
    ```console
    $ python3 start-publish.py
    ```

*The above scripts are written for `bash` on Windows Subsystem for Linux 2 (WSL2), hence recommend using UNIX systems for compatibility.*

## Run on Windows without WSL2
1. Run on PowerShell
    ```powershell
    > python3 -m venv venv

    > . .\venv\scripts\activate

    > pip install -r requirements.txt

    > python3 manage.py migrate

    > python3 manage.py runserver
    ```

2. Run on new PowerShell terminal
    ```powershell
    > cd client

    > npm start
    ```
