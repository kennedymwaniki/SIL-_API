import os
import sys
import django
from django.conf import settings

# Add the project root directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Configure Django settings before any tests are run
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Initialize Django
def pytest_configure():
    django.setup()