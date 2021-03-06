# Strader
Strader contains:
 - Endpoint to let users place trades. Quantity of the stock the user wants to buy or sell is recorded.
 - Endpoint to retrieve total value invested in a single stock by user.
 - Endpoint to retrieve the total value invested by user in his/her account.


# Initial setup (local)
Run the `start-env.sh` script to setup the initial environment.


# Running test
Run `python manage.py test` to execute the implemented test cases.


# API Documentation
This is using `drf-yasg` to provide the API documentations. After running the server in your local,
docs can be accessed using [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/) or [http://127.0.0.1:8000/docs/](http://127.0.0.1:8000/docs).


# Authentication
Strader uses JWT for user authentication. To call an API, each request must contain
access token in their request authorization header using [http://127.0.0.1:8000/api/token/](http://127.0.0.1:8000/api/token/).
