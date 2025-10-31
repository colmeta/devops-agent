"""
Environment Setup Wizard
Automatically creates .env file with all credentials for clarity-pearl-production
"""

import os
import json
from pathlib import Path
from datetime import datetime
import getpass

class EnvSetupWizard:
    """Interactive wizard to setup all environment variables"""
    
    def __init__(self):
        self.credentials = {}
        self.project_path = self.find_project()
        
    def find_project(self):
        """Find clarity-pearl-production"""
        possible_paths = [
            "C:/Users/LENOVO/Desktop/clarity-pearl-production",
            os.path.expanduser("~/Desktop/clarity-pearl-production"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"✅ Found project: {path}")
                return path
        
        path = input("Enter path to clarity-pearl-production: ").strip()
        return path if os.path.exists(path) else None
    
    def load_devops_credentials(self):
        """Load credentials from devops-agent"""
        if os.path.exists('credentials.json'):
            try:
                with open('credentials.json', 'r') as f:
                    creds = json.load(f)
                    
                devops_creds = {}
                for cred in creds:
                    key = f"{cred['service'].upper()}_{cred['key_name'].upper()}"
                    devops_creds[key] = cred['value']
                
                print(f"\n✅ Loaded {len(devops_creds)} credentials from devops-agent")
                return devops_creds
            except Exception as e:
                print(f"⚠️  Could not load devops credentials: {e}")
        return {}
    
    def prompt_for_credential(self, key, description, default=None, secret=False):
        """Prompt user for a credential"""
        print(f"\n📝 {description}")
        
        if default:
            print(f"   Current/Default: {default[:20]}..." if len(str(default)) > 20 else f"   Current/Default: {default}")
        
        if secret:
            value = getpass.getpass(f"   Enter {key} (or press Enter to skip): ")
        else:
            value = input(f"   Enter {key} (or press Enter to skip): ").strip()
        
        return value if value else default
    
    def collect_database_credentials(self):
        """Collect database credentials"""
        print("\n" + "="*70)
        print("💾 DATABASE CONFIGURATION")
        print("="*70)
        
        print("\n📌 PostgreSQL Connection String Format:")
        print("   postgresql://username:password@host:port/database")
        print("   Example: postgresql://user:pass@localhost:5432/clarity_db")
        
        self.credentials['POSTGRES_URL'] = self.prompt_for_credential(
            'POSTGRES_URL',
            'PostgreSQL Connection String',
            secret=True
        )
    
    def collect_ai_credentials(self):
        """Collect AI API credentials"""
        print("\n" + "="*70)
        print("🤖 AI API CREDENTIALS")
        print("="*70)
        
        # OpenAI
        print("\n🔹 OpenAI API Key")
        print("   Get from: https://platform.openai.com/api-keys")
        self.credentials['OPENAI_API_KEY'] = self.prompt_for_credential(
            'OPENAI_API_KEY',
            'OpenAI API Key (starts with sk-)',
            secret=True
        )
        
        # Anthropic
        print("\n🔹 Anthropic API Key")
        print("   Get from: https://console.anthropic.com/settings/keys")
        self.credentials['ANTHROPIC_API_KEY'] = self.prompt_for_credential(
            'ANTHROPIC_API_KEY',
            'Anthropic API Key (starts with sk-ant-)',
            secret=True
        )
        
        # Groq
        print("\n🔹 Groq API Key")
        print("   Get from: https://console.groq.com/keys")
        self.credentials['GROQ_API_KEY'] = self.prompt_for_credential(
            'GROQ_API_KEY',
            'Groq API Key',
            secret=True
        )
    
    def collect_twilio_credentials(self):
        """Collect Twilio credentials"""
        print("\n" + "="*70)
        print("📞 TWILIO VOICE CONFIGURATION")
        print("="*70)
        
        print("\n📌 Get these from: https://console.twilio.com/")
        
        self.credentials['TWILIO_ACCOUNT_SID'] = self.prompt_for_credential(
            'TWILIO_ACCOUNT_SID',
            'Twilio Account SID (starts with AC)',
            secret=False
        )
        
        self.credentials['TWILIO_AUTH_TOKEN'] = self.prompt_for_credential(
            'TWILIO_AUTH_TOKEN',
            'Twilio Auth Token',
            secret=True
        )
        
        self.credentials['TWILIO_PHONE_NUMBER'] = self.prompt_for_credential(
            'TWILIO_PHONE_NUMBER',
            'Twilio Phone Number (format: +1234567890)',
            secret=False
        )
    
    def collect_meta_credentials(self, devops_creds):
        """Collect Meta WhatsApp credentials"""
        print("\n" + "="*70)
        print("📱 META WHATSAPP BUSINESS API")
        print("="*70)
        
        # Check if we have them from devops-agent
        if devops_creds:
            print("\n✅ Found Meta credentials from devops-agent!")
            
            if 'META_ACCESS_TOKEN' in devops_creds:
                self.credentials['META_ACCESS_TOKEN'] = devops_creds['META_ACCESS_TOKEN']
                print(f"   ✓ Access Token: {devops_creds['META_ACCESS_TOKEN'][:20]}...")
            
            if 'META_APP_SECRET' in devops_creds:
                self.credentials['META_APP_SECRET'] = devops_creds['META_APP_SECRET']
                print(f"   ✓ App Secret: {devops_creds['META_APP_SECRET'][:20]}...")
            
            if 'META_VERIFY_TOKEN' in devops_creds:
                self.credentials['META_VERIFY_TOKEN'] = devops_creds['META_VERIFY_TOKEN']
                print(f"   ✓ Verify Token: {devops_creds['META_VERIFY_TOKEN'][:20]}...")
            
            if 'META_PHONE_NUMBER_ID' in devops_creds:
                self.credentials['WHATSAPP_PHONE_NUMBER_ID'] = devops_creds['META_PHONE_NUMBER_ID']
                print(f"   ✓ Phone Number ID: {devops_creds['META_PHONE_NUMBER_ID']}")
            
            update = input("\n   Update any Meta credentials? (y/n): ").lower()
            if update != 'y':
                return
        
        # Manual entry if needed
        print("\n📌 Get these from: https://developers.facebook.com/apps/")
        
        if 'META_ACCESS_TOKEN' not in self.credentials or not self.credentials['META_ACCESS_TOKEN']:
            self.credentials['META_ACCESS_TOKEN'] = self.prompt_for_credential(
                'META_ACCESS_TOKEN',
                'Meta Access Token',
                secret=True
            )
        
        if 'META_APP_SECRET' not in self.credentials or not self.credentials['META_APP_SECRET']:
            self.credentials['META_APP_SECRET'] = self.prompt_for_credential(
                'META_APP_SECRET',
                'Meta App Secret',
                secret=True
            )
        
        if 'META_VERIFY_TOKEN' not in self.credentials or not self.credentials['META_VERIFY_TOKEN']:
            self.credentials['META_VERIFY_TOKEN'] = self.prompt_for_credential(
                'META_VERIFY_TOKEN',
                'Meta Verify Token',
                secret=False
            )
        
        if 'WHATSAPP_PHONE_NUMBER_ID' not in self.credentials or not self.credentials['WHATSAPP_PHONE_NUMBER_ID']:
            self.credentials['WHATSAPP_PHONE_NUMBER_ID'] = self.prompt_for_credential(
                'WHATSAPP_PHONE_NUMBER_ID',
                'WhatsApp Phone Number ID (15 digits)',
                secret=False
            )
    
    def collect_google_credentials(self, devops_creds):
        """Collect Google OAuth credentials"""
        print("\n" + "="*70)
        print("🔐 GOOGLE OAUTH (Calendar, Gmail)")
        print("="*70)
        
        # Check devops-agent first
        default_client_id = devops_creds.get('GOOGLE_OAUTH_CLIENT_ID')
        default_client_secret = devops_creds.get('GOOGLE_OAUTH_CLIENT_SECRET')
        
        if default_client_id:
            print(f"\n✅ Found from devops-agent: {default_client_id[:30]}...")
        
        print("\n📌 Get from: https://console.cloud.google.com/apis/credentials")
        
        self.credentials['GOOGLE_CLIENT_ID'] = self.prompt_for_credential(
            'GOOGLE_CLIENT_ID',
            'Google Client ID',
            default=default_client_id,
            secret=False
        )
        
        self.credentials['GOOGLE_CLIENT_SECRET'] = self.prompt_for_credential(
            'GOOGLE_CLIENT_SECRET',
            'Google Client Secret',
            default=default_client_secret,
            secret=True
        )
    
    def collect_microsoft_credentials(self, devops_creds):
        """Collect Microsoft OAuth credentials"""
        print("\n" + "="*70)
        print("🔐 MICROSOFT OAUTH (Outlook Calendar)")
        print("="*70)
        
        # Check devops-agent first
        default_client_id = devops_creds.get('MICROSOFT_OAUTH_CLIENT_ID')
        default_client_secret = devops_creds.get('MICROSOFT_OAUTH_CLIENT_SECRET')
        
        if default_client_id:
            print(f"\n✅ Found from devops-agent: {default_client_id[:30]}...")
        
        print("\n📌 Get from: https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps")
        
        self.credentials['MICROSOFT_CLIENT_ID'] = self.prompt_for_credential(
            'MICROSOFT_CLIENT_ID',
            'Microsoft Client ID',
            default=default_client_id,
            secret=False
        )
        
        self.credentials['MICROSOFT_CLIENT_SECRET'] = self.prompt_for_credential(
            'MICROSOFT_CLIENT_SECRET',
            'Microsoft Client Secret',
            default=default_client_secret,
            secret=True
        )
    
    def collect_vector_db_credentials(self):
        """Collect vector database credentials"""
        print("\n" + "="*70)
        print("🗄️ VECTOR DATABASES")
        print("="*70)
        
        # Pinecone
        print("\n🔹 Pinecone")
        print("   Get from: https://app.pinecone.io/")
        self.credentials['PINECONE_API_KEY'] = self.prompt_for_credential(
            'PINECONE_API_KEY',
            'Pinecone API Key',
            secret=True
        )
        
        # Weaviate
        print("\n🔹 Weaviate")
        print("   Get from: https://console.weaviate.cloud/")
        self.credentials['WEAVIATE_ENDPOINT'] = self.prompt_for_credential(
            'WEAVIATE_ENDPOINT',
            'Weaviate Endpoint URL',
            default='https://your-cluster.weaviate.network',
            secret=False
        )
        
        self.credentials['WEAVIATE_API_KEY'] = self.prompt_for_credential(
            'WEAVIATE_API_KEY',
            'Weaviate API Key',
            secret=True
        )
    
    def collect_misc_credentials(self):
        """Collect miscellaneous credentials"""
        print("\n" + "="*70)
        print("⚙️ ADDITIONAL CONFIGURATION")
        print("="*70)
        
        self.credentials['ROUTER_API_URL'] = self.prompt_for_credential(
            'ROUTER_API_URL',
            'LLM Router API URL',
            default='http://localhost:8000',
            secret=False
        )
    
    def generate_env_file(self):
        """Generate the .env file"""
        if not self.project_path:
            print("❌ No project path found!")
            return
        
        env_path = os.path.join(self.project_path, '.env')
        
        # Backup existing .env if it exists
        if os.path.exists(env_path):
            backup_path = f"{env_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.rename(env_path, backup_path)
            print(f"\n📦 Backed up existing .env to: {backup_path}")
        
        # Generate content
        content = [
            "# Environment Variables for Clarity Pearl Production",
            f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "# IMPORTANT: Never commit this file to git!",
            "",
            "# ==========================================",
            "# DATABASE",
            "# ==========================================",
            f"POSTGRES_URL={self.credentials.get('POSTGRES_URL', '')}",
            "",
            "# ==========================================",
            "# AI APIS",
            "# ==========================================",
            f"OPENAI_API_KEY={self.credentials.get('OPENAI_API_KEY', '')}",
            f"ANTHROPIC_API_KEY={self.credentials.get('ANTHROPIC_API_KEY', '')}",
            f"GROQ_API_KEY={self.credentials.get('GROQ_API_KEY', '')}",
            "",
            "# ==========================================",
            "# TWILIO VOICE",
            "# ==========================================",
            f"TWILIO_ACCOUNT_SID={self.credentials.get('TWILIO_ACCOUNT_SID', '')}",
            f"TWILIO_AUTH_TOKEN={self.credentials.get('TWILIO_AUTH_TOKEN', '')}",
            f"TWILIO_PHONE_NUMBER={self.credentials.get('TWILIO_PHONE_NUMBER', '')}",
            "",
            "# ==========================================",
            "# META WHATSAPP BUSINESS API",
            "# ==========================================",
            f"META_ACCESS_TOKEN={self.credentials.get('META_ACCESS_TOKEN', '')}",
            f"META_APP_SECRET={self.credentials.get('META_APP_SECRET', '')}",
            f"META_VERIFY_TOKEN={self.credentials.get('META_VERIFY_TOKEN', '')}",
            f"WHATSAPP_PHONE_NUMBER_ID={self.credentials.get('WHATSAPP_PHONE_NUMBER_ID', '')}",
            "",
            "# ==========================================",
            "# GOOGLE OAUTH (Calendar, Gmail)",
            "# ==========================================",
            f"GOOGLE_CLIENT_ID={self.credentials.get('GOOGLE_CLIENT_ID', '')}",
            f"GOOGLE_CLIENT_SECRET={self.credentials.get('GOOGLE_CLIENT_SECRET', '')}",
            "",
            "# ==========================================",
            "# MICROSOFT OAUTH (Outlook Calendar)",
            "# ==========================================",
            f"MICROSOFT_CLIENT_ID={self.credentials.get('MICROSOFT_CLIENT_ID', '')}",
            f"MICROSOFT_CLIENT_SECRET={self.credentials.get('MICROSOFT_CLIENT_SECRET', '')}",
            "",
            "# ==========================================",
            "# VECTOR DATABASES",
            "# ==========================================",
            f"PINECONE_API_KEY={self.credentials.get('PINECONE_API_KEY', '')}",
            f"WEAVIATE_ENDPOINT={self.credentials.get('WEAVIATE_ENDPOINT', '')}",
            f"WEAVIATE_API_KEY={self.credentials.get('WEAVIATE_API_KEY', '')}",
            "",
            "# ==========================================",
            "# ADDITIONAL CONFIGURATION",
            "# ==========================================",
            f"ROUTER_API_URL={self.credentials.get('ROUTER_API_URL', 'http://localhost:8000')}",
            ""
        ]
        
        # Write file
        try:
            with open(env_path, 'w') as f:
                f.write('\n'.join(content))
            
            print(f"\n✅ Successfully created .env file!")
            print(f"   Location: {env_path}")
            
            # Count non-empty values
            filled = sum(1 for v in self.credentials.values() if v)
            total = len(self.credentials)
            print(f"   Credentials filled: {filled}/{total}")
            
            if filled < total:
                print(f"\n⚠️  {total - filled} credentials are empty. You can:")
                print("     1. Run this wizard again")
                print("     2. Manually edit the .env file")
                print("     3. Run devops_agent.py to extract more credentials")
            
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
    
    def run(self):
        """Run the complete wizard"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║  Environment Setup Wizard                                     ║
║  Let's setup all your credentials!                           ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        if not self.project_path:
            print("❌ Could not find project!")
            return
        
        print(f"\n📂 Project: {self.project_path}")
        
        # Load existing credentials from devops-agent
        devops_creds = self.load_devops_credentials()
        
        print("\n" + "="*70)
        print("🚀 QUICK START OPTIONS")
        print("="*70)
        print("\n1. Full Setup (all credentials)")
        print("2. Only essential credentials (AI APIs, Database, Twilio)")
        print("3. Only Meta/Google/Microsoft OAuth")
        print("4. Custom selection")
        
        choice = input("\nChoose option (1-4): ").strip()
        
        if choice == "1":
            # Full setup
            self.collect_database_credentials()
            self.collect_ai_credentials()
            self.collect_twilio_credentials()
            self.collect_meta_credentials(devops_creds)
            self.collect_google_credentials(devops_creds)
            self.collect_microsoft_credentials(devops_creds)
            self.collect_vector_db_credentials()
            self.collect_misc_credentials()
            
        elif choice == "2":
            # Essential only
            self.collect_database_credentials()
            self.collect_ai_credentials()
            self.collect_twilio_credentials()
            self.collect_misc_credentials()
            
        elif choice == "3":
            # OAuth only
            self.collect_meta_credentials(devops_creds)
            self.collect_google_credentials(devops_creds)
            self.collect_microsoft_credentials(devops_creds)
            
        elif choice == "4":
            # Custom
            print("\nSelect what to configure (y/n for each):")
            
            if input("  Database? (y/n): ").lower() == 'y':
                self.collect_database_credentials()
            
            if input("  AI APIs? (y/n): ").lower() == 'y':
                self.collect_ai_credentials()
            
            if input("  Twilio? (y/n): ").lower() == 'y':
                self.collect_twilio_credentials()
            
            if input("  Meta WhatsApp? (y/n): ").lower() == 'y':
                self.collect_meta_credentials(devops_creds)
            
            if input("  Google OAuth? (y/n): ").lower() == 'y':
                self.collect_google_credentials(devops_creds)
            
            if input("  Microsoft OAuth? (y/n): ").lower() == 'y':
                self.collect_microsoft_credentials(devops_creds)
            
            if input("  Vector Databases? (y/n): ").lower() == 'y':
                self.collect_vector_db_credentials()
            
            if input("  Misc Config? (y/n): ").lower() == 'y':
                self.collect_misc_credentials()
        
        # Generate the file
        self.generate_env_file()
        
        print("\n" + "="*70)
        print("✅ SETUP COMPLETE!")
        print("="*70)
        print("\n💡 Next steps:")
        print("   1. Review the .env file")
        print("   2. Test your application")
        print("   3. Run env_extractor.py option 5 to verify")
        print("\n⚠️  SECURITY:")
        print("   • Never commit .env to git")
        print("   • Keep backups secure")
        print("   • Rotate keys regularly")


if __name__ == "__main__":
    wizard = EnvSetupWizard()
    wizard.run()