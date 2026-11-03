import os
import sys
from pathlib import Path

# Add root directory to sys.path so Django can resolve imports
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edubridge.settings')
application = get_wsgi_application()

# Wrap with WhiteNoise to ensure static files are served seamlessly on Vercel
static_root = BASE_DIR / 'staticfiles'
static_dir = BASE_DIR / 'static'

if static_root.exists():
    application = WhiteNoise(application, root=str(static_root), prefix='static/')
else:
    application = WhiteNoise(application, root=str(static_dir), prefix='static/')

if static_dir.exists():
    application.add_files(str(static_dir), prefix='static/')

# Vercel entrypoint variable
app = application
