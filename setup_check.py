"""
Setup verification script
Checks if all required dependencies and configurations are in place
"""

import os
from dotenv import load_dotenv
from pathlib import Path

def check_env_file():
    """Check if .env file exists"""
    if not Path('.env').exists():
        print("❌ .env file not found")
        print("   → Copy .example.env to .env and add your API keys")
        return False
    print("✅ .env file exists")
    return True

def check_api_keys():
    """Check if required API keys are set"""
    load_dotenv()

    required_keys = {
        'SUPABASE_URL': os.getenv('SUPABASE_URL'),
        'SUPABASE_KEY': os.getenv('SUPABASE_KEY'),
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY')
    }

    all_set = True
    for key, value in required_keys.items():
        if not value or value.startswith('xxx') or value.startswith('your-'):
            print(f"❌ {key} not configured")
            all_set = False
        else:
            print(f"✅ {key} configured")

    return all_set

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit',
        'pydantic_ai',
        'supabase',
        'docling',
        'google.generativeai'
    ]

    all_installed = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} installed")
        except ImportError:
            print(f"❌ {package} not installed")
            all_installed = False

    return all_installed

def check_supabase_connection():
    """Test Supabase connection"""
    try:
        from supabase_utils import SupabaseManager
        db = SupabaseManager()
        print("✅ Supabase connection successful")
        return True
    except Exception as e:
        print(f"❌ Supabase connection failed: {str(e)}")
        return False

def check_gemini_api():
    """Test Gemini API"""
    try:
        import google.generativeai as genai
        api_key = os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=api_key)

        # Test embedding generation
        result = genai.embed_content(
            model="models/text-embedding-004",
            content="test",
            task_type="retrieval_document"
        )
        print("✅ Gemini API working")
        return True
    except Exception as e:
        print(f"❌ Gemini API failed: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("Company Q&A Chatbot - Setup Verification")
    print("=" * 60)
    print()

    print("📋 Checking configuration files...")
    env_ok = check_env_file()
    print()

    if not env_ok:
        print("⚠️  Please create .env file before continuing")
        return

    print("🔑 Checking API keys...")
    keys_ok = check_api_keys()
    print()

    if not keys_ok:
        print("⚠️  Please configure all API keys in .env file")
        print()

    print("📦 Checking dependencies...")
    deps_ok = check_dependencies()
    print()

    if not deps_ok:
        print("⚠️  Please install dependencies:")
        print("   pip install -r requirements.txt")
        print()

    if keys_ok and deps_ok:
        print("🔌 Testing connections...")
        print()

        print("Testing Supabase...")
        supabase_ok = check_supabase_connection()
        print()

        print("Testing Gemini API...")
        gemini_ok = check_gemini_api()
        print()
    else:
        supabase_ok = False
        gemini_ok = False

    print("=" * 60)
    print("Summary")
    print("=" * 60)

    all_ok = env_ok and keys_ok and deps_ok and supabase_ok and gemini_ok

    if all_ok:
        print("🎉 All checks passed! You're ready to go.")
        print()
        print("Next steps:")
        print("1. Run: streamlit run app.py")
        print("2. Go to Admin tab and upload a PDF")
        print("3. Go to User tab and ask questions")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print()
        print("Setup guide:")
        print("1. Create .env file from .example.env")
        print("2. Add your API keys to .env")
        print("3. Run SQL schema in Supabase: supabase_schema.sql")
        print("4. Install dependencies: pip install -r requirements.txt")
        print("5. Run this script again to verify")

    print("=" * 60)

if __name__ == "__main__":
    main()
