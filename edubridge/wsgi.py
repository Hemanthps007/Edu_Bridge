import os
import sys
from pathlib import Path

# Add root directory to sys.path so Django can resolve imports
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edubridge.settings')
application = get_wsgi_application()
