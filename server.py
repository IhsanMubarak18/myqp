#!/usr/bin/env python3
"""
Server startup script for Question Paper Generator Desktop App
This script starts the Django development server and handles initialization
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    """Start Django server for desktop application"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'question_paper_project.settings')
    
    # Initialize Django
    django.setup()
    
    # Run migrations on first start
    from django.core.management import call_command
    try:
        print("Checking database migrations...")
        call_command('migrate', '--noinput')
        print("Database ready!")
    except Exception as e:
        print(f"Migration warning: {e}")
    
    # Start the server
    # Port will be passed as command line argument from Electron
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
