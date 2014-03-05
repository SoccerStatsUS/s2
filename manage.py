
#!/usr/bin/env python
import os
import sys

from custom_settings import DEBUG

if DEBUG is False or os.path.exists("/Users"):
    prefix = 's2'
else:
    prefix = 'sdev'


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "%s.settings" % prefix)

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
