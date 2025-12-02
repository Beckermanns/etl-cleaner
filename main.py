from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Configuramos la carpeta donde están los HTML
templates = Jinja2Templates(directory="templates")

@app.get("/")
def home(request: Request):
    # En lugar de devolver JSON, devolvemos la plantilla index.html
    return templates.TemplateResponse("index.html", {"request": request})