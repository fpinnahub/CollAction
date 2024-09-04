## prossimi passi

### debug

### Set an env file
Create a `.env` file at the same level of "app/" folder, where set all 
your environment variables. For example:
```makefile
SECRET_KEY=mysecretkey123
```
Remember to **not commit** this file.


### How to register a new user
From a python console, just import:
`import app.commands.register_user`

You'll be asked to enter "username" and "password".


### How to delete a user and all related tables
From a python console, just import:
`import app.commands.delete_user`

You'll be asked for the username


## How to run CollAction
From outside `app` folder, run:
```python
python app/main.py
```