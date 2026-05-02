import os
import boto3
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from dotenv import load_dotenv

load_dotenv()

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")

s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
)


def generar_pdf(nota: dict) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, f"Nota de Venta - {nota['folio']}")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Fecha: {nota['fecha_creacion']}")
    c.drawString(50, height - 100, f"Cliente ID: {nota['cliente_id']}")
    c.drawString(50, height - 120, f"Dirección Facturación ID: {nota['direccion_facturacion_id']}")
    c.drawString(50, height - 140, f"Dirección Envío ID: {nota['direccion_envio_id']}")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 170, "Contenido:")

    y = height - 190
    c.setFont("Helvetica", 11)
    for item in nota["contenido"]:
        linea = (
            f"  Producto ID: {item['producto_id']} | "
            f"Cantidad: {item['cantidad']} | "
            f"Precio Unitario: ${item['precio_unitario']:.2f} | "
            f"Importe: ${item['importe']:.2f}"
        )
        c.drawString(50, y, linea)
        y -= 20

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y - 10, f"Total: ${nota['total']:.2f}")

    c.save()
    buffer.seek(0)
    return buffer


def subir_pdf_a_s3(folio: str, pdf_buffer: BytesIO) -> str:
    key = f"notas/{folio}.pdf"
    s3_client.upload_fileobj(
        pdf_buffer,
        S3_BUCKET_NAME,
        key,
        ExtraArgs={"ContentType": "application/pdf"},
    )
    return key


def generar_url_descarga(folio: str, expiracion: int = 3600) -> str:
    key = f"notas/{folio}.pdf"
    url = s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": S3_BUCKET_NAME, "Key": key},
        ExpiresIn=expiracion,
    )
    return url
