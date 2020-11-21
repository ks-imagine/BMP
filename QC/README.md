# BMP | Quality Control API

BMP QC API repository. uWu


## Getting Started

### Prerequisites

Kindly ensure you have the following installed:
- [ ] [Python 3.6](https://www.python.org/downloads/release/python-365/)
- [ ] [Pip](https://pip.pypa.io/en/stable/installing/)
- [ ] [Virtualenv](https://virtualenv.pypa.io/en/stable/installation/)
- [ ] [PostgreSQL](https://www.postgresql.org/)

### Setting up + Running

1. Clone the repo:

    ```
    $ git clone https://github.com/ks-imagine/BMP.git
    $ cd QC
    ```

2. With Python 3.6 and Pip installed:

    ```
    $ virtualenv --python=python3 env --no-site-packages
    $ source env/bin/activate
    $ pip install -r requirements.txt
    ```

3. Create a PostgreSQL user with the username and password `postgres` and create a database called `bmp-qc-api`:

    ```
    $ createuser --interactive --pwprompt
    $ createdb qc_api
    ```

4. Export the required environment variables:

    ```
    $ export FLASK_APP=app.py
    ```

5. Execute the migrations to create the `products` table:

    ```
    $ flask db init
    $ flask db migrate
    $ flask db upgrade
    ```

6. Run the Flask API:

    ```
    $ flask run
    ```

7. Navigate to `http://localhost:5000/products` to view the products data.