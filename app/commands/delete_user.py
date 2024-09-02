from db_utils import delete_user

try:
    username = input('Inserisci il nome dell\'utente da cancellare:')

    delete_user(username)

    print(f'Utente {username} e tutte le tabelle collegate sono stati cancellati correttamente!')
except Exception as e:
    print(e)
    print('Operazione fallita')
