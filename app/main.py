import uvicorn
import models, database
from typing import List
from fastapi import FastAPI, Depends, HTTPException, Request, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from utils import collation_html_from_dict, dictfy_witness_text
from consts import LEMMATIZERS

app = FastAPI()

# Aggiungi il middleware CORS per permettere richieste dal frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.get("/lemmatizers/", response_model=List[str])
async def get_lemmatizers():

    return LEMMATIZERS


@app.post("/add_witness/")
async def add_witness(
        request: AddWitnessRequest, db: Session = Depends(get_db)
):
    new_witness = models.Witness(
        name=request.witness_name, text=request.witness_text
    )
    db.add(new_witness)
    db.commit()
    db.refresh(new_witness)

    witnesses = db.query(models.Witness).all()

    return {"witnesses": [{"id": w.id, "name": w.name} for w in witnesses]}


@app.get("/get_witnesses/", response_class=JSONResponse)
async def get_witnesses(db: Session = Depends(get_db)):
    witnesses = db.query(models.Witness).all()

    return [{"id": w.id, "name": w.name} for w in witnesses]


@app.post("/delete_witness/")
async def delete_witness(request: DeleteWitnessRequest, db: Session = Depends(get_db)):
    witness = db.query(models.Witness).filter(models.Witness.id == request.witness_id).first()
    if witness:
        db.delete(witness)
        db.commit()

        return {"status": "Testimone rimosso con successo!"}
    else:

        raise HTTPException(status_code=404, detail="Testimone non trovato")


@app.get("/collation/", response_class=HTMLResponse)
async def get_collation(request: Request, lemmatizer, db: Session = Depends(get_db)):
    selected_lemmatizer = lemmatizer    # per adesso, non utilizzato
    witnesses = db.query(models.Witness).all()
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

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "collation_html": html_table,
            "collation_title": "Risultato della Collazione"
        }
    )


# API POST per salvare una tabella di collazione nel DB
@app.post("/save_collation/")
async def save_collation(
        name: str = Body(...), html_table: str = Body(...), db: Session = Depends(get_db)
):
    existing = db.query(models.Collation).filter(models.Collation.name == name).first()
    if existing:

        raise HTTPException(status_code=400, detail="Una collazione con questo nome esiste già.")

    new_collation = models.Collation(name=name, html_table=html_table)
    db.add(new_collation)
    db.commit()

    return {"message": "Collazione salvata con successo"}


# API POST per cancellare una tabella di collazione dal DB
@app.post("/delete_collation/")
async def delete_collation(request: CollationTableRequest, db: Session = Depends(get_db)):
    collation = db.query(models.Collation).filter(models.Collation.name == request.name).first()
    if collation:
        db.delete(collation)
        db.commit()

        return {"message": "Collazione rimossa con successo"}

    raise HTTPException(status_code=404, detail="Collazione non trovata")


# API POST per caricare una tabella di collazione dal DB
@app.post("/load_collation/")
async def load_collation(request: CollationTableRequest, db: Session = Depends(get_db)):
    collation = db.query(models.Collation).filter(
        models.Collation.name == request.name
    ).first()
    if collation:

        return {"name": collation.name, "html_table": collation.html_table}

    raise HTTPException(status_code=404, detail="Collazione non trovata")


# API GET per ottenere la lista di tutte le tabelle di collazione nel DB
@app.get("/get_collations/")
async def get_collations(db: Session = Depends(get_db)):
    collations = db.query(models.Collation).all()

    return [{"name": collation.name} for collation in collations]


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):

    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
