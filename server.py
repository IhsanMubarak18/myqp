import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    port = sys.argv[1] if len(sys.argv) > 1 else "8000"

    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "question_paper_project.settings"
    )

    django.setup()

    try:
        from django.core.management import call_command
        call_command("migrate", interactive=False)
    except Exception as e:
        print("Migration warning:", e)

    execute_from_command_line([
        "manage.py",
        "runserver",
        f"127.0.0.1:{port}",
        "--noreload"
    ])
