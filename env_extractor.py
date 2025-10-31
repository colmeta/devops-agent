"""
Environment Variable Extractor for Clarity Pearl Production
Automatically extracts and manages environment variables from your chatbot project
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnvExtractor:
    """Extract and manage environment variables for clarity-pearl-production"""
    
    def __init__(self, project_path: str = None):
        self.project_path = project_path or self.find_project()
        self.env_vars = {}
        self.vault_path = "clarity_env_vault.json"
        
    def find_project(self) -> str:
        """Try to find clarity-pearl-production directory"""
        print("\n🔍 Looking for clarity-pearl-production project...")
        
        # Common locations
        possible_paths = [
            "C:/Users/LENOVO/Desktop/clarity-pearl-production",
            os.path.expanduser("~/Desktop/clarity-pearl-production"),
            "C:/Users/LENOVO/clarity-pearl-production",
            "../clarity-pearl-production",
            "../../clarity-pearl-production",
            os.path.join(os.path.dirname(os.getcwd()), "clarity-pearl-production")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"✅ Found project at: {path}")
                confirm = input(f"Use this path? (y/n): ").strip().lower()
                if confirm == 'y':
                    return path
        
        # Ask user
        print("\n📁 Project not auto-detected.")
        print("Common locations:")
        print("  • C:/Users/LENOVO/clarity-pearl-production")
        print("  • If it's elsewhere, enter the full path")
        
        path = input("\nEnter path to clarity-pearl-production (or 'exit' to quit): ").strip()
        
        if path.lower() == 'exit':
            return None
        
        if os.path.exists(path):
            return path
        else:
            logger.error("❌ Project not found at that path!")
            retry = input("Try again? (y/n): ").strip().lower()
            if retry == 'y':
                return self.find_project()
            return None
    
    def scan_for_env_vars(self) -> Dict[str, List[str]]:
        """Scan project files for environment variable usage"""
        if not self.project_path:
            logger.error("❌ No project path set")
            return {}
        
        env_pattern = re.compile(r'process\.env\.(\w+)|os\.getenv\([\'"](\w+)[\'"]\)')
        found_vars = {}
        
        logger.info("🔍 Scanning project for environment variables...")
        
        # Scan all Python and JavaScript files
        for root, dirs, files in os.walk(self.project_path):
            # Skip node_modules, venv, etc.
            dirs[:] = [d for d in dirs if d not in ['node_modules', 'venv', '.git', '__pycache__']]
            
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.jsx', '.tsx')):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            matches = env_pattern.findall(content)
                            
                            for match in matches:
                                var_name = match[0] or match[1]
                                if var_name:
                                    if var_name not in found_vars:
                                        found_vars[var_name] = []
                                    rel_path = os.path.relpath(filepath, self.project_path)
                                    found_vars[var_name].append(rel_path)
                    except Exception as e:
                        logger.debug(f"Could not read {filepath}: {e}")
        
        logger.info(f"✅ Found {len(found_vars)} environment variables")
        return found_vars
    
    def read_existing_env(self) -> Dict[str, str]:
        """Read existing .env file from clarity-pearl-production"""
        env_file = os.path.join(self.project_path, '.env')
        env_vars = {}
        
        if not os.path.exists(env_file):
            logger.warning("⚠️  No .env file found in project")
            return env_vars
        
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
            
            logger.info(f"✅ Read {len(env_vars)} variables from .env")
            return env_vars
            
        except Exception as e:
            logger.error(f"❌ Error reading .env: {e}")
            return {}
    
    def categorize_env_vars(self, env_vars: Dict[str, str]) -> Dict[str, Dict[str, str]]:
        """Categorize environment variables by service"""
        categories = {
            'meta': {},
            'google': {},
            'microsoft': {},
            'openai': {},
            'anthropic': {},
            'database': {},
            'flowise': {},
            'render': {},
            'other': {}
        }
        
        for key, value in env_vars.items():
            key_lower = key.lower()
            
            if any(x in key_lower for x in ['meta', 'facebook', 'whatsapp', 'instagram']):
                categories['meta'][key] = value
            elif any(x in key_lower for x in ['google', 'gmail', 'gcal']):
                categories['google'][key] = value
            elif any(x in key_lower for x in ['microsoft', 'outlook', 'azure']):
                categories['microsoft'][key] = value
            elif 'openai' in key_lower or 'gpt' in key_lower:
                categories['openai'][key] = value
            elif 'anthropic' in key_lower or 'claude' in key_lower:
                categories['anthropic'][key] = value
            elif any(x in key_lower for x in ['database', 'db', 'postgres', 'mongo']):
                categories['database'][key] = value
            elif 'flowise' in key_lower:
                categories['flowise'][key] = value
            elif 'render' in key_lower:
                categories['render'][key] = value
            else:
                categories['other'][key] = value
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def generate_env_template(self, used_vars: Dict[str, List[str]]) -> str:
        """Generate .env.example with documentation"""
        template = [
            "# Environment Variables for Clarity Pearl Production",
            f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "# ==========================================",
            "# INSTRUCTIONS:",
            "# 1. Copy this file to .env",
            "# 2. Fill in your actual values",
            "# 3. NEVER commit .env to git",
            "# ==========================================",
            ""
        ]
        
        # Read existing values
        existing = self.read_existing_env()
        
        # Categorize
        categories = self.categorize_env_vars(existing)
        
        category_names = {
            'meta': 'Meta/WhatsApp Business API',
            'google': 'Google Services (OAuth, Gmail, etc)',
            'microsoft': 'Microsoft Services (Outlook, Azure)',
            'openai': 'OpenAI API',
            'anthropic': 'Anthropic/Claude API',
            'database': 'Database Configuration',
            'flowise': 'Flowise AI',
            'render': 'Render Deployment',
            'other': 'Other Configuration'
        }
        
        for category, vars_dict in categories.items():
            if vars_dict:
                template.append(f"\n# {category_names.get(category, category.upper())}")
                template.append("# " + "-" * 50)
                
                for key, value in sorted(vars_dict.items()):
                    # Add usage info if available
                    if key in used_vars:
                        files = used_vars[key][:3]  # Show max 3 files
                        template.append(f"# Used in: {', '.join(files)}")
                    
                    # Mask sensitive values
                    if value and not value.startswith('your_'):
                        if len(value) > 20:
                            display_value = f"your_{key.lower()}_here"
                        else:
                            display_value = f"your_{key.lower()}"
                    else:
                        display_value = value or f"your_{key.lower()}"
                    
                    template.append(f"{key}={display_value}")
                    template.append("")
        
        return "\n".join(template)
    
    def save_to_vault(self, env_vars: Dict[str, str]):
        """Save environment variables to encrypted vault"""
        vault_data = {
            'project': 'clarity-pearl-production',
            'updated_at': datetime.now().isoformat(),
            'variables': env_vars,
            'count': len(env_vars)
        }
        
        try:
            with open(self.vault_path, 'w') as f:
                json.dump(vault_data, f, indent=2)
            logger.info(f"✅ Saved {len(env_vars)} variables to vault")
        except Exception as e:
            logger.error(f"❌ Error saving vault: {e}")
    
    def load_from_vault(self) -> Dict[str, str]:
        """Load environment variables from vault"""
        if not os.path.exists(self.vault_path):
            return {}
        
        try:
            with open(self.vault_path, 'r') as f:
                data = json.load(f)
                return data.get('variables', {})
        except Exception as e:
            logger.error(f"❌ Error loading vault: {e}")
            return {}
    
    def update_env_file(self, updates: Dict[str, str]):
        """Update .env file with new values"""
        if not self.project_path:
            logger.error("❌ No project path set")
            return
        
        env_file = os.path.join(self.project_path, '.env')
        existing = self.read_existing_env()
        
        # Merge updates
        existing.update(updates)
        
        try:
            with open(env_file, 'w') as f:
                f.write(f"# Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                categorized = self.categorize_env_vars(existing)
                
                for category, vars_dict in categorized.items():
                    f.write(f"\n# {category.upper()}\n")
                    for key, value in sorted(vars_dict.items()):
                        f.write(f"{key}={value}\n")
            
            logger.info(f"✅ Updated .env file with {len(updates)} new values")
            
        except Exception as e:
            logger.error(f"❌ Error updating .env: {e}")
    
    def compare_with_devops_credentials(self):
        """Compare clarity-pearl credentials with devops-agent extracted ones"""
        logger.info("🔄 Comparing credentials...")
        
        # Load devops-agent credentials
        devops_creds = {}
        if os.path.exists('credentials.json'):
            with open('credentials.json', 'r') as f:
                creds = json.load(f)
                for cred in creds:
                    key = f"{cred['service'].upper()}_{cred['key_name'].upper()}"
                    devops_creds[key] = cred['value']
        
        # Load clarity-pearl .env
        clarity_env = self.read_existing_env()
        
        # Find missing in clarity-pearl
        missing = {}
        for key, value in devops_creds.items():
            if key not in clarity_env or not clarity_env[key]:
                missing[key] = value
        
        if missing:
            logger.info(f"\n📋 Found {len(missing)} variables that can be added:")
            for key in missing.keys():
                logger.info(f"   • {key}")
            
            if input("\nAdd these to clarity-pearl-production? (y/n): ").lower() == 'y':
                self.update_env_file(missing)
        else:
            logger.info("✅ All devops-agent credentials are already in clarity-pearl-production")
    
    def generate_report(self):
        """Generate comprehensive environment variable report"""
        logger.info("\n" + "="*70)
        logger.info("ENVIRONMENT VARIABLE REPORT")
        logger.info("="*70)
        
        # Scan for usage
        used_vars = self.scan_for_env_vars()
        
        # Read existing
        existing = self.read_existing_env()
        
        # Categorize
        categories = self.categorize_env_vars(existing)
        
        logger.info(f"\n📊 Statistics:")
        logger.info(f"   Total variables defined: {len(existing)}")
        logger.info(f"   Variables in use: {len(used_vars)}")
        logger.info(f"   Categories: {len(categories)}")
        
        logger.info(f"\n📋 By Category:")
        for category, vars_dict in categories.items():
            logger.info(f"   {category}: {len(vars_dict)} variables")
        
        # Find unused
        unused = set(existing.keys()) - set(used_vars.keys())
        if unused:
            logger.info(f"\n⚠️  Potentially unused variables ({len(unused)}):")
            for var in list(unused)[:5]:
                logger.info(f"   • {var}")
            if len(unused) > 5:
                logger.info(f"   ... and {len(unused) - 5} more")
        
        # Find missing (used but not defined)
        missing = set(used_vars.keys()) - set(existing.keys())
        if missing:
            logger.info(f"\n❌ Missing variables ({len(missing)}):")
            for var in missing:
                files = used_vars[var][:2]
                logger.info(f"   • {var} (used in: {', '.join(files)})")
        
        logger.info("\n" + "="*70)


def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║  Environment Variable Extractor                               ║
║  For Clarity Pearl Production                                ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    extractor = EnvExtractor()
    
    if not extractor.project_path:
        logger.error("❌ Cannot proceed without project path")
        input("\nPress Enter to exit...")
        return
    
    while True:
        print(f"""
📂 Project: {extractor.project_path}

What would you like to do?

1. 📊 Scan and analyze environment variables
2. 📝 Generate .env.example template
3. 🔄 Sync with devops-agent credentials
4. 💾 Save current .env to vault
5. 📋 Generate full report
6. Exit
""")
        
        choice = input("Enter choice (1-6): ").strip()
        
        if choice == "1":
            used_vars = extractor.scan_for_env_vars()
            existing = extractor.read_existing_env()
            
            print(f"\n✅ Found {len(used_vars)} variables in code")
            print(f"✅ Found {len(existing)} variables in .env")
            
        elif choice == "2":
            used_vars = extractor.scan_for_env_vars()
            template = extractor.generate_env_template(used_vars)
            
            output_file = os.path.join(extractor.project_path, '.env.example')
            with open(output_file, 'w') as f:
                f.write(template)
            
            print(f"\n✅ Generated {output_file}")
            print(f"   {len(template.split(chr(10)))} lines written")
            
        elif choice == "3":
            extractor.compare_with_devops_credentials()
            
        elif choice == "4":
            env_vars = extractor.read_existing_env()
            extractor.save_to_vault(env_vars)
            print(f"\n✅ Saved {len(env_vars)} variables to {extractor.vault_path}")
            
        elif choice == "5":
            extractor.generate_report()
            
        elif choice == "6":
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid choice. Please enter 1-6")
            continue
        
        input("\nPress Enter to continue...")
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()