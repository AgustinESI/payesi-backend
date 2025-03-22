The command `python test_db.py` checks if the database connection is okey.

To change the information related to the database you have to change the values in `config.py`

```
set FLASK_APP=run.py

flask db init             # Starts the migration
flask db migrate -m "Initialize the database"
flask db upgrade          # Applies migrations
```

Execute command `.venv\Scripts\activate` to start the enviorement
