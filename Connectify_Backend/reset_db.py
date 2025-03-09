import os
import django
from django.db import connection

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Connectify_Backend.settings')
django.setup()

# Get cursor
with connection.cursor() as cursor:
    # Get all tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    # Drop all tables
    if tables:
        print(f"Dropping tables: {', '.join(tables)}")
        cursor.execute(f"DROP TABLE {', '.join(tables)} CASCADE")
        print("All tables dropped successfully.")
    else:
        print("No tables to drop.")

print("Database reset complete. Now run 'python manage.py migrate' to recreate the tables.") 