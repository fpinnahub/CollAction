import sys
from pathlib import Path

# set "app/" as working directory
cwd = Path(__file__)
sys.path.append(cwd.parents[1].__str__())


from db_utils import register


try:
    username = input('Inserisci il nome del nuovo utente da registrare:')
    password = input('Inserisci la password:')

    register(username, password)

    print(f'Utente {username} aggiunto correttamente!')
except Exception as e:
    print(e)
    print('Operazione fallita')
