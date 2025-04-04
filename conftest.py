import os
import sys
import django
from django.conf import settings

# Add the project root directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Configure Django settings before any tests are run
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Set a default SECRET_KEY for testing
os.environ.setdefault("SECRET_KEY", "django-insecure-test-key-for-testing-only")

# Initialize Django
def pytest_configure():
    django.setup()
    
    # Set up the test database by running migrations
    from django.core.management import call_command
    call_command('migrate')