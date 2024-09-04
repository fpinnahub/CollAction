import os
import uvicorn
import models, database
from security import verify_password, get_password_hash
from typing import List
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, Request, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from utils import collation_html_from_dict, dictfy_witness_text
from consts import LEMMATIZERS

app = FastAPI()

# Monta la directory static
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Aggiungi il middleware per le sessioni con una chiave segreta
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "default-secret-key"))

# Aggiungi il middleware CORS per permettere richieste dal frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware personalizzato per intercettare l'errore 401 e reindirizzare
class RedirectToLoginMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        if response.status_code == 401:  # Se l'utente non è autenticato

            return RedirectResponse(url="/login")  # Reindirizza alla pagina di login

        return response


app.add_middleware(RedirectToLoginMiddleware)


templates = Jinja2Templates(directory="app/templates")


# Definiamo uno schema per la richiesta di rimozione Testimoni
class DeleteWitnessRequest(BaseModel):
    witness_id: int


class AddWitnessRequest(BaseModel):
    witness_name: str
    witness_text: str


class CollationRequest(BaseModel):
    lemmatizer: str


class CollationTableRequest(BaseModel):
    name: str


# Dependency per ottenere la sessione DB
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Funzione per ottenere l'utente corrente dalla sessione e dal DB
def get_current_user(request: Request, db: Session = Depends(get_db)):
    username: str = request.session.get('user')
    if not username:

        raise HTTPException(status_code=401, detail="Not authenticated")
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:

        raise HTTPException(status_code=401, detail="User not found")

    return user


# Rotte per l'autenticazione
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):

    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(
        request: Request, db: Session = Depends(get_db), username: str = Form(...),
        password: str = Form(...)
):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):

        raise HTTPException(status_code=400, detail="Invalid credentials")
    request.session['user'] = user.username

    return RedirectResponse(url="/", status_code=303)


@app.post("/logout")
async def logout(request: Request):
    request.session.clear()

    return RedirectResponse(url="/login", status_code=302)


# Rotte esistenti, protette con autenticazione
@app.post("/change_password/")
async def change_password(
    request: Request,
    db: Session = Depends(get_db),
    current_password: str = Body(...),
    new_password: str = Body(...),
    user: models.User = Depends(get_current_user)
):
    # Verifica che la password attuale sia corretta
    if not verify_password(current_password, user.hashed_password):

        raise HTTPException(status_code=400, detail="La password attuale è errata.")

    # Aggiorna la password con quella nuova
    user.hashed_password = get_password_hash(new_password)
    db.commit()

    return {"message": "Password aggiornata con successo."}


@app.get("/lemmatizers/", response_model=List[str])
async def get_lemmatizers(user: models.User = Depends(get_current_user)):  # Protegge questa rotta

    return LEMMATIZERS


@app.post("/add_witness/")
async def add_witness(
        request: AddWitnessRequest, db: Session = Depends(get_db),
        user: models.User = Depends(get_current_user)
):
    new_witness = models.Witness(
        name=request.witness_name, text=request.witness_text
    )
    db.add(new_witness)
    db.commit()
    db.refresh(new_witness)

    # Show only witness for the current user
    u_id: int = user.id
    witnesses = db.query(models.Witness).filter(models.Witness.owner_id == u_id).all()

    return {"witnesses": [{"id": w.id, "name": w.name} for w in witnesses]}


@app.get("/get_witnesses/", response_class=JSONResponse)
async def get_witnesses(
        db: Session = Depends(get_db), user: models.User = Depends(get_current_user)
):
    u_id: int = user.id
    witnesses = db.query(models.Witness).filter(models.Witness.owner_id == u_id).all()

    return [{"id": w.id, "name": w.name} for w in witnesses]


@app.post("/delete_witness/")
async def delete_witness(
        request: DeleteWitnessRequest, db: Session = Depends(get_db),
        user: models.User = Depends(get_current_user)
):
    witness = db.query(models.Witness).filter(models.Witness.id == request.witness_id).first()
    if witness:
        db.delete(witness)
        db.commit()

        return {"status": "Testimone rimosso con successo!"}
    else:

        raise HTTPException(status_code=404, detail="Testimone non trovato")


@app.get("/collation/", response_class=HTMLResponse)
async def get_collation(
        request: Request, lemmatizer, db: Session = Depends(get_db),
        user: models.User = Depends(get_current_user)
):
    selected_lemmatizer = lemmatizer    # per adesso, non utilizzato
    u_id: int = user.id
    witnesses = db.query(models.Witness).filter(models.Witness.owner_id == u_id).all()
    if len(witnesses) < 2:

        raise HTTPException(status_code=500, detail="Servono almeno due testimoni")

    # Ottieni i dati dei testimoni
    data = {
        'witnesses': [
            dictfy_witness_text(w.text, w.name) for w in witnesses
        ]
    }

    # Ottieni l'HTML della tabella
    html_table = collation_html_from_dict(data)

    return JSONResponse(content=jsonable_encoder({"collation_html": html_table}))


# API POST per salvare una tabella di collazione nel DB
@app.post("/save_collation/")
async def save_collation(
        name: str = Body(...), html_table: str = Body(...), db: Session = Depends(get_db),
        user: models.User = Depends(get_current_user)
):
    u_id: int = user.id
    existing = db.query(models.Collation).filter(
        models.Collation.name == name,
        models.Collation.owner_id == u_id
    ).first()
    if existing:

        raise HTTPException(status_code=400, detail="Una collazione con questo nome esiste già.")

    new_collation = models.Collation(name=name, html_table=html_table, owner_id=user.id)
    db.add(new_collation)
    db.commit()

    return {"message": "Collazione salvata con successo"}


# API POST per cancellare una tabella di collazione dal DB
@app.post("/delete_collation/")
async def delete_collation(
        request: CollationTableRequest, db: Session = Depends(get_db),
        user: models.User = Depends(get_current_user)
):
    u_id: int = user.id
    collation = db.query(models.Collation).filter(
        models.Collation.name == request.name,
        models.Collation.owner_id == u_id
    ).first()
    if collation:
        db.delete(collation)
        db.commit()

        return {"message": "Collazione rimossa con successo"}

    raise HTTPException(status_code=404, detail="Collazione non trovata")


# API POST per caricare una tabella di collazione dal DB
@app.post("/load_collation/")
async def load_collation(
        request: CollationTableRequest, db: Session = Depends(get_db),
        user: models.User = Depends(get_current_user)
):
    u_id: int = user.id
    collation = db.query(models.Collation).filter(
        models.Collation.name == request.name,
        models.Collation.owner_id == u_id
    ).first()
    if collation:

        return {"name": collation.name, "html_table": collation.html_table}

    raise HTTPException(status_code=404, detail="Collazione non trovata")


# API GET per ottenere la lista di tutte le tabelle di collazione nel DB
@app.get("/get_collations/")
async def get_collations(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    u_id: int = user.id
    collations = db.query(models.Collation).filter(models.Collation.owner_id == u_id).all()

    return [{"name": collation.name} for collation in collations]


@app.get("/", response_class=HTMLResponse)
def home(request: Request, user: models.User = Depends(get_current_user)):

    return templates.TemplateResponse(
        "index.html", {"request": request, "username": user.username}
    )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
