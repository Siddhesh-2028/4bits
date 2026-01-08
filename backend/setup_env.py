"""
Quick script to help you find your Supabase Anon Key

1. Go to: https://supabase.com/dashboard/project/fdmfyhsumhxokcobyscq/settings/api
2. Look for "Project API keys" section
3. Copy the "anon" key (NOT the service_role key)
4. Paste it below

Then run: python setup_env.py
"""

import os

def setup_env():
    print("="  * 60)
    print("VITA-Care Environment Setup")
    print("=" * 60)
    print()
    
    # Get Supabase key from user
    print("📋 Please provide your Supabase Anon Key:")
    print("   (Find it at: Project Settings > API > anon key)")
    print()
    supabase_key = input("Paste Supabase Anon Key here: ").strip()
    
    if not supabase_key or len(supabase_key) < 20:
        print("❌ Invalid key. Please try again.")
        return
    
    # Optional: Get Gemini API key
    print()
    print("📋 Gemini API Key (optional,press Enter to skip):")
    gemini_key = input("Paste Gemini API Key (or press Enter): ").strip()
    
    # Create .env file
    env_content = f"""# Gemini API Key
GEMINI_API_KEY={gemini_key if gemini_key else 'your_gemini_api_key_here'}

# Supabase Credentials
SUPABASE_URL=https://fdmfyhsumhxokcobyscq.supabase.co
SUPABASE_KEY={supabase_key}
SUPABASE_PASSWORD=gGngRRXW4odtxDLH

# JWT Secret
JWT_SECRET=vita-care-hackathon-2026-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
"""
    
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(env_content)
    
    print()
    print("✅ .env file created successfully!")
    print(f"   Location: {env_path}")
    print()
    print("🧪 Testing Supabase connection...")
    
    # Test connection
    try:
        from supabase_client import test_connection
        if test_connection():
            print()
            print("🎉 Setup complete! You can now:")
            print("   1. Run backend: python main.py")
            print("   2. Run frontend: cd ../frontend && npm run dev")
        else:
            print()
            print("⚠️  Connection test failed. Please check your Supabase key.")
    except Exception as e:
        print(f)
        print(f"⚠️  Error testing connection: {e}")
        print("   But .env file was created. Try running: python main.py")


if __name__ == "__main__":
    setup_env()
