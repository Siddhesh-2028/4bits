"""
Supabase Client Configuration
Initializes and provides Supabase client instance
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase_client: Client = None

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables. Please add it to .env file.")

try:
    supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase client initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize Supabase client: {e}")
    raise


def get_supabase_client() -> Client:
    """
    Get the Supabase client instance
    
    Returns:
        Supabase client
    """
    return supabase_client


def test_connection() -> bool:
    """
    Test Supabase connection
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        # Try to query patients table
        result = supabase_client.table("patients").select("count", count="exact").limit(0).execute()
        print(f"✅ Connected to Supabase successfully!")
        print(f"   Patients count: {result.count}")
        return True
    except Exception as e:
        print(f"❌ Supabase connection test failed: {e}")
        return False


if __name__ == "__main__":
    print("Testing Supabase connection...")
    test_connection()
