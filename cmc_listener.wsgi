#!/usr/bin/python
import sys

path = "/home/yourusername/mysite"
if path not in sys.path:
    sys.path.insert(0, path)

from app import app as application