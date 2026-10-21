import sqlite3
import json
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, Any

app = FastAPI(title="Motor Cautare Piese Auto (FTS5 + Faceted Search)")

conn = sqlite3.connect(":memory:", check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("""
    CREATE VIRTUAL TABLE produse USING fts5(
        titlu, 
        descriere, 
        marca UNINDEXED, 
        pret UNINDEXED, 
        atribute UNINDEXED
    )
""")

produse_test = [
    ("Disc frana fata Brembo", "Disc ventilat performanta ridicata", "Dacia", 250, '{"diametru_mm": 260, "ventilat": "Da"}'),
    ("Disc frana spate Bosch", "Disc plin standard din fonta", "Dacia", 180, '{"diametru_mm": 240, "ventilat": "Nu"}'),
    ("Placute frana ATE", "Placute ceramice fara praf pentru fata", "Volkswagen", 300, '{"material": "ceramic", "senzor_uzura": "Da"}'),
    ("Bec far Osram H7", "Bec halogen lumina alba puternica", "Dacia", 45, '{"soclu": "H7", "putere_W": 55}'),
    ("Bec far Philips LED", "Bec rece tehnologie LED pentru far", "Volkswagen", 150, '{"soclu": "H4", "putere_W": 20}')
]
cursor.executemany("INSERT INTO produse VALUES (?, ?, ?, ?, ?)", produse_test)
conn.commit()

class CautareRequest(BaseModel):
    text: Optional[str] = None
    marca: Optional[str] = None
    filtre_dinamice: Dict[str, Any] = {}

@app.post("/cauta")
def cauta_produse(cerere: CautareRequest):
    query = "SELECT rowid, * FROM produse WHERE 1=1"
    params = []

    if cerere.text:
        query += " AND produse MATCH ?"
        params.append(cerere.text)

    if cerere.marca:
        query += " AND marca = ?"
        params.append(cerere.marca)

    for cheie, valoare in cerere.filtre_dinamice.items():
        query += f" AND json_extract(atribute, '$.{cheie}') = ?"
        params.append(valoare)

    if cerere.text:
        query += " ORDER BY rank"

    rezultate_db = cursor.execute(query, params).fetchall()

    produse_gasite = []
    filtre_disponibile = {}

    for row in rezultate_db:
        atribute_dict = json.loads(row["atribute"])
        produse_gasite.append({
            "id": row["rowid"],
            "titlu": row["titlu"],
            "descriere": row["descriere"],
            "marca": row["marca"],
            "pret": row["pret"],
            "atribute": atribute_dict
        })

        for k, v in atribute_dict.items():
            if k not in filtre_disponibile:
                filtre_disponibile[k] = []
            if v not in filtre_disponibile[k]:
                filtre_disponibile[k].append(v)

    return {
        "total_gasite": len(produse_gasite),
        "filtre_dinamice_disponibile": filtre_disponibile,
        "produse": produse_gasite
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("elastic_search:app", host="127.0.0.1", port=8000, reload=True)