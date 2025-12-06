from fastapi import FastAPI, Request, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse
import pandas as pd
import io

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def process_data(file: UploadFile = File(...)):
    # 1. LEER EL ARCHIVO EN MEMORIA
    contents = await file.read()
    
    # Convertimos los bytes a un "archivo virtual" para que Pandas lo entienda
    buffer = io.BytesIO(contents)
    
    try:
        # Intentamos leer como CSV
        df = pd.read_csv(buffer)
    except:
        return {"error": "Por favor sube un archivo CSV válido."}

    # 2. APLICAR LIMPIEZA (Lógica de Negocio)
    # Aquí es donde tu SaaS aporta valor. Por ahora haremos una limpieza básica:
    
    # a) Eliminar filas completamente vacías
    df.dropna(how="all", inplace=True)
    
    # b) Eliminar duplicados exactos
    df.drop_duplicates(inplace=True)
    
    # c) "Strip" de textos (eliminar espacios al inicio y final de las celdas tipo texto)
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # 3. PREPARAR LA DESCARGA
    # Creamos un nuevo buffer para guardar el resultado limpio
    output_buffer = io.BytesIO()
    
    # Guardamos el DataFrame limpio en ese buffer (sin el índice numérico)
    df.to_csv(output_buffer, index=False)
    
    # "Rebobinamos" el buffer al principio para poder leerlo
    output_buffer.seek(0)

    # 4. DEVOLVER EL ARCHIVO
    # StreamingResponse permite descargar el archivo generado al vuelo
    return StreamingResponse(
        output_buffer, 
        media_type="text/csv", 
        headers={"Content-Disposition": f"attachment; filename=limpio_{file.filename}"}
    )