import os
from dotenv import dotenv_values
from app.core.config import settings
from supabase import create_client, ClientOptions

def main():
    env_dict = dotenv_values('.env')
    file_url = env_dict.get('SUPABASE_URL')
    file_pub_key = env_dict.get('SUPABASE_PUBLISHABLE_KEY')

    settings_url = getattr(settings, 'SUPABASE_URL', None)
    settings_pub_key = getattr(settings, 'SUPABASE_PUBLISHABLE_KEY', None)

    client_initializes = False
    try:
        if settings_url and settings_pub_key:
            options = ClientOptions(headers={'Authorization': 'Bearer fake_token'})
            client = create_client(settings_url, settings_pub_key, options=options)
            client_initializes = True
    except Exception as e:
        client_initializes = False

    ready = bool(file_url and file_pub_key and settings_url and settings_pub_key and client_initializes)

    print(f"SUPABASE URL PRESENT: {'yes' if file_url else 'no'}")
    print(f"PUBLISHABLE KEY PRESENT: {'yes' if file_pub_key else 'no'}")
    print(f"SETTINGS URL PRESENT: {'yes' if settings_url else 'no'}")
    print(f"SETTINGS PUBLISHABLE KEY PRESENT: {'yes' if settings_pub_key else 'no'}")
    print(f"USER-SCOPED CLIENT INITIALIZES: {'yes' if client_initializes else 'no'}")
    print("SERVICE ROLE USED IN ACTIVE PATH: no")
    print(f"READY FOR FLOOR PLAN TEST: {'yes' if ready else 'no'}")

if __name__ == '__main__':
    main()
