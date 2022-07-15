# Portfolio Tracker
Web application developed for Code To Connect 2022 – FICC Problem Statement

<br>

Recommended environment:
1. Python 3.8+
2. Node.js 16 LTS

<br>

## Starting up
### 1. Start the server application
1. Run

    ```console
    $ bash start.sh
    ```

2. Keep this terminal running to provide data for the client UI

### 2. Start the client UI
1. Run on a new terminal
    ```console
    $ bash client.sh
    ```

2. Open [`localhost:3000`](http://localhost:3000) in a browser to see the client interface

### 3. Publish events to see changes
These scripts emulate sending market data or trade events to the server, by periodically making POST requests to server, with event details as payload.
1. Run on a new terminal
    ```console
    $ python3 publish-market-data.py
    ```
2. Run on yet another terminal
    ```console
    $ python3 publish-trade-events.py
    ```

*The above scripts are written for `bash` on Windows Subsystem for Linux 2 (WSL2), hence recommend using UNIX systems for compatibility.*

<br>

## Staring on Windows without WSL2
1. Run on PowerShell
    ```powershell
    > python3 -m venv venv

    > . .\venv\scripts\activate

    > pip install -r requirements.txt

    > rm db.sqlite3

    > python3 manage.py migrate

    > python3 manage.py runserver
    ```

2. Run on new PowerShell terminal
    ```powershell
    > cd client

    > npm start
    ```

3. Run on new terminals
     ```powershell
    >  python3 publish-market-data.py
    ```
    and
     ```powershell
    >  python3 publish-trade-events.py
    ```

<br>

## Input and Output directories
Input data at `data/`

Output reports at `out/output_*/`

## App implementation details
1. Embedded database:
    sqlite3 with Django ORM with models defined in: `api/models.py`

2. Required components:
    1. Market Data Producer:
    `publish-market-data.py`

    2. Trade Event Data Producer:
    `publish-trade-events.py`

    3. Portfolio Engine:
    `event_handler/event_handlers.py`

    4. Cash Adjuster:
    `event_handler/cash_adjuster.py`

    5. Report Generator:
    `report_generator/portfolio_generator`
    and
    `report_generator/report_generator`
