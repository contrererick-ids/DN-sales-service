import os
import time
import boto3
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION")
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")

cloudwatch = boto3.client(
    "cloudwatch",
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
)

NAMESPACE = "SalesService"


def registrar_conteo_http(status_code: int):
    if 200 <= status_code < 300:
        rango = "2xx"
    elif 400 <= status_code < 500:
        rango = "4xx"
    else:
        rango = "5xx"

    cloudwatch.put_metric_data(
        Namespace=NAMESPACE,
        MetricData=[
            {
                "MetricName": "HTTPResponseCount",
                "Dimensions": [
                    {"Name": "Environment", "Value": ENVIRONMENT},
                    {"Name": "StatusRange", "Value": rango},
                ],
                "Timestamp": datetime.now(timezone.utc),
                "Value": 1,
                "Unit": "Count",
            }
        ],
    )


def registrar_tiempo_ejecucion(duracion_ms: float):
    cloudwatch.put_metric_data(
        Namespace=NAMESPACE,
        MetricData=[
            {
                "MetricName": "EndpointDuration",
                "Dimensions": [
                    {"Name": "Environment", "Value": ENVIRONMENT},
                    {"Name": "Endpoint", "Value": "POST /notas"},
                ],
                "Timestamp": datetime.now(timezone.utc),
                "Value": duracion_ms,
                "Unit": "Milliseconds",
            }
        ],
    )
