import sys
import os

# Ensure we can import app
sys.path.insert(0, os.getcwd())

from app import consolidator

print(f"Imported consolidator module: {consolidator}")
print(f"MODEL_NAME in module: {consolidator.MODEL_NAME}")

if hasattr(consolidator, 'generate_summary'):
    print("generate_summary function exists.")
else:
    print("generate_summary missing.")
