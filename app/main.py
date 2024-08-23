import uvicorn

import models, database
from fastapi import FastAPI, Depends, HTTPException, Request, Form, Body
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from utils import collation_html_from_dict, dictfy_witness_text

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")


# Definiamo uno schema per la richiesta di rimozione Testimoni
class DeleteWitnessRequest(BaseModel):
    witness_id: int


# Dependency per ottenere la sessione DB
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/add_witness/")
async def add_witness(
        name: str = Form(...), text: str = Form(...), db: Session = Depends(get_db)
):
    new_witness = models.Witness(name=name, text=text)
    db.add(new_witness)
    db.commit()
    db.refresh(new_witness)

    return {"status": "Witness has been added!"}


@app.get("/get_witnesses/", response_class=JSONResponse)
async def get_witnesses(db: Session = Depends(get_db)):
    witnesses = db.query(models.Witness).all()

    return [{"id": w.id, "name": w.name} for w in witnesses]


@app.post("/delete_witness/")
async def delete_witness(request: DeleteWitnessRequest, db: Session = Depends(get_db)):
    print('delete_witness')
    witness = db.query(models.Witness).filter(models.Witness.id == request.witness_id).first()
    if witness:
        db.delete(witness)
        db.commit()

        return {"status": "Testimone rimosso con successo!"}
    else:

        raise HTTPException(status_code=404, detail="Testimone non trovato")


@app.get("/collation/", response_class=HTMLResponse)
async def get_collation(request: Request, db: Session = Depends(get_db)):
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
        # "index.html", {"request": db, "collation_html": html_table}
        "index.html", {"request": request, "collation_html": html_table}
    )


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):

    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
