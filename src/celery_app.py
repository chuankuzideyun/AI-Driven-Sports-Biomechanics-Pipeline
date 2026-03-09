import os
from celery import Celery

# Use environment variable with a local fallback for native testing
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

celery_instance = Celery(
    'Magic_tasks',
    broker=redis_url,
    backend=redis_url
)