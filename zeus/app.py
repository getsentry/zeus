"""
This file acts as a default entry point for app creation.
"""

from .config import celery, create_app

app = create_app()

celery = celery.get_celery_app()
