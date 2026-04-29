from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import Base, engine, get_db
from app.errors import http_exception_handler, generic_exception_handler
from app.service import TokenizationService

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tokenization Service", version="1.0.0")

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/tokenize")
def tokenize(account_numbers: list[str], db: Session = Depends(get_db)):
    service = TokenizationService(db)
    return service.tokenize(account_numbers)


@app.post("/detokenize")
def detokenize(tokens: list[str], db: Session = Depends(get_db)):
    service = TokenizationService(db)
    return service.detokenize(tokens)
