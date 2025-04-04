#!/usr/bin/env python
import os
import sys
import coverage
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    # Configure coverage before importing any app code
    cov = coverage.Coverage(
        source=['api'],
        omit=[
            '*/migrations/*',
            '*/tests/*',
            '*/test_*.py',
            '*/__init__.py',
            '*/admin.py',
            '*/apps.py',
        ]
    )
    cov.start()

    # Setup Django and run tests
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # If no arguments are provided, run all tests
    test_labels = sys.argv[1:] or ['api']
    
    failures = test_runner.run_tests(test_labels)
    
    # Generate coverage report
    cov.stop()
    cov.save()
    
    print('Coverage Summary:')
    cov.report()
    
    # Generate HTML report
    html_dir = os.path.join('coverage_html')
    cov.html_report(directory=html_dir)
    print(f'HTML report generated in {html_dir}/')
    
    sys.exit(bool(failures))