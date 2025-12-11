from app import app
from vercel_wsgi import handle


def handler(request, context):
    return handle(app, request, context)
