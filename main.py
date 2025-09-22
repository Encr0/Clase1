from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import mysql.connector
from mysql.connector import Error

app = FastAPI(title="Demo API CRUD MySQL Usuarios")
templates = Jinja2Templates(directory="Clase1/templates")

class Usuario(BaseModel):
    nombre: str
    fecha_inicio: str  # formato: "YYYY-MM-DD"
    rut: str

def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="un2"
        )
        if not conn.is_connected():
            raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
        return conn
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error conectando a la base de datos: {str(e)}")

# Endpoints API JSON
@app.post("/usuarios/")
def crear_usuario(usuario: Usuario):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO usuarios (nombre, fecha_inicio, rut) VALUES (%s, %s, %s)",
        (usuario.nombre, usuario.fecha_inicio, usuario.rut)
    )
    conn.commit()
    user_id = cur.lastrowid
    cur.close()
    conn.close()
    return {"id": user_id, "msg": "usuario creado"}

@app.get("/usuarios/")
def listar_usuarios():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, nombre, fecha_inicio, rut FROM usuarios")
    usuarios = cur.fetchall()
    cur.close()
    conn.close()
    return usuarios

# Endpoint para servir formulario registro y procesar datos
@app.get("/register", response_class=HTMLResponse)
def get_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register(
    rut: str = Form(...),
    nombre: str = Form(...),
    fecha_inicio: str = Form(...)
):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO usuarios (nombre, fecha_inicio, rut) VALUES (%s, %s, %s)",
            (nombre, fecha_inicio, rut)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Error guardando usuario: {str(e)}")
    finally:
        cur.close()
        conn.close()

    return {"msg": "Usuario registrado correctamente"}
