import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app import models
from app import schemas
from app.database import get_db
from app.services.s3_service import generar_pdf, subir_pdf_a_s3, generar_url_descarga
from app.services.sns_service import publicar_notificacion
from app.services.metrics_service import registrar_conteo_http, registrar_tiempo_ejecucion
import os
import time


router = APIRouter(prefix="/notas", tags=["Notas"])

CATALOGS_SERVICE_URL = os.getenv("CATALOGS_SERVICE_URL", "http://localhost:8001")


def validar_cliente(cliente_id: int):
    try:
        response = httpx.get(f"{CATALOGS_SERVICE_URL}/clientes/{cliente_id}")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Cliente no encontrado en catálogos")
        return response.json()
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Catálogos service no disponible")


def validar_domicilio(domicilio_id: int):
    try:
        response = httpx.get(f"{CATALOGS_SERVICE_URL}/domicilios/{domicilio_id}")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Domicilio no encontrado en catálogos")
        return response.json()
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Catálogos service no disponible")


def validar_producto(producto_id: int):
    try:
        response = httpx.get(f"{CATALOGS_SERVICE_URL}/productos/{producto_id}")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Producto no encontrado en catálogos")
        return response.json()
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Catálogos service no disponible")


@router.get("/", response_model=list[schemas.NotaResponse])
def listar_notas(db: Session = Depends(get_db)):
    return db.query(models.Nota).all()


@router.get("/{nota_id}", response_model=schemas.NotaResponse)
def obtener_nota(nota_id: int, db: Session = Depends(get_db)):
    nota = db.query(models.Nota).filter(models.Nota.id == nota_id).first()
    if not nota:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    return nota


@router.post("/", response_model=schemas.NotaResponse, status_code=201)
def crear_nota(nota: schemas.NotaCreate, db: Session = Depends(get_db)):
    inicio = time.time()
    status_code = 201

    try:
        cliente = validar_cliente(nota.cliente_id)
        validar_domicilio(nota.direccion_facturacion_id)
        validar_domicilio(nota.direccion_envio_id)

        total = 0.0
        contenido_validado = []

        for item in nota.contenido:
            validar_producto(item.producto_id)
            importe = item.cantidad * item.precio_unitario
            total += importe
            contenido_validado.append({**item.model_dump(), "importe": importe})

        ultimo_id = db.query(models.Nota).count() + 1
        folio = f"NV-{ultimo_id:04d}"

        db_nota = models.Nota(
            folio=folio,
            cliente_id=nota.cliente_id,
            direccion_facturacion_id=nota.direccion_facturacion_id,
            direccion_envio_id=nota.direccion_envio_id,
            total=total,
        )
        db.add(db_nota)
        db.commit()
        db.refresh(db_nota)

        for item in contenido_validado:
            db_contenido = models.ContenidoNota(
                nota_id=db_nota.id,
                **item,
            )
            db.add(db_contenido)
        db.commit()
        db.refresh(db_nota)

        nota_dict = {
            "folio": db_nota.folio,
            "fecha_creacion": str(db_nota.fecha_creacion),
            "cliente_id": db_nota.cliente_id,
            "direccion_facturacion_id": db_nota.direccion_facturacion_id,
            "direccion_envio_id": db_nota.direccion_envio_id,
            "total": float(db_nota.total),
            "contenido": contenido_validado,
        }

        pdf_buffer = generar_pdf(nota_dict)
        subir_pdf_a_s3(folio, pdf_buffer)
        url_descarga = generar_url_descarga(folio)

        publicar_notificacion(folio, db_nota.cliente_id, float(db_nota.total), url_descarga)

        return db_nota

    except HTTPException as e:
        status_code = e.status_code
        raise

    except Exception as e:
        status_code = 500
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        duracion_ms = (time.time() - inicio) * 1000
        registrar_tiempo_ejecucion(duracion_ms)
        registrar_conteo_http(status_code)


@router.get("/{folio}/descargar")
def descargar_nota(folio: str):
    url = generar_url_descarga(folio)
    return RedirectResponse(url=url)
