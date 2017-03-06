# Application
 -  Test application using JSON Web Token managed Login.
 - check `JWT_ACCESS_TOKEN_EXPIRES` and `JWT_REFRESH_TOKEN_EXPIRES` in `config.py`
 - `JWT_ACCESS_TOKEN_EXPIRES` to set the expiration of the token
 - `JWT_REFRESH_TOKEN_EXPIRES` to set the expiration of refreshed token [/refresh [POST]]

# Get environment ready
 - pip install -r requirements.txt

# Export configurations into envron

- export APP_SETTINGS="config.DevelopmentConfig"
- export DATABASE_URL="postgresql+psycopg2://<username>:<password>@localhost:5432/workout"

# run the application

- ./run.py

TODOs
- Exceptions handling
- Model Serialization
- Mailer via event listner and queuing
- Unit Tests
- Code Refactoring 