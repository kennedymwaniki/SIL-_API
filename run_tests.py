#!/usr/bin/env python
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # If no arguments are provided, run all tests
    test_labels = sys.argv[1:] or ['api']
    
    # You can add specific test modules or classes
    # e.g.: python run_tests.py api.tests.CustomerModelTests
    
    failures = test_runner.run_tests(test_labels)
    sys.exit(bool(failures))