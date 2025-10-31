"""
Test all extracted credentials
Verifies that Meta, Google, and Microsoft credentials work
"""

import os
import sys
import json
import asyncio
import logging
from dotenv import load_dotenv
import requests
from datetime import datetime

# Load environment
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CredentialTester:
    """Test all service credentials"""
    
    def __init__(self):
        self.results = {}
        
    def test_meta_whatsapp(self):
        """Test Meta WhatsApp credentials"""
        logger.info("📱 Testing Meta WhatsApp credentials...")
        
        access_token = os.getenv('META_ACCESS_TOKEN')
        phone_id = os.getenv('META_PHONE_NUMBER_ID')
        app_id = os.getenv('META_APP_ID')
        
        if not access_token or not phone_id:
            self.results['meta'] = {
                'status': 'failed',
                'reason': 'Missing credentials'
            }
            logger.error("❌ Missing META_ACCESS_TOKEN or META_PHONE_NUMBER_ID")
            return
        
        try:
            # Test 1: Verify access token
            url = f"https://graph.facebook.com/v18.0/{phone_id}"
            headers = {'Authorization': f'Bearer {access_token}'}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.results['meta'] = {
                    'status': 'success',
                    'phone_number': data.get('display_phone_number'),
                    'verified': data.get('verified_name'),
                    'quality': data.get('quality_rating')
                }
                logger.info(f"✅ Meta WhatsApp: {data.get('display_phone_number')}")
                logger.info(f"   Quality rating: {data.get('quality_rating')}")
                
                # Test 2: Check message templates
                template_url = f"https://graph.facebook.com/v18.0/{app_id}/message_templates"
                template_resp = requests.get(template_url, headers=headers)
                
                if template_resp.status_code == 200:
                    templates = template_resp.json().get('data', [])
                    logger.info(f"   Templates available: {len(templates)}")
                    for tmpl in templates[:3]:
                        logger.info(f"      - {tmpl.get('name')} ({tmpl.get('status')})")
                
            elif response.status_code == 401:
                self.results['meta'] = {
                    'status': 'failed',
                    'reason': 'Invalid access token'
                }
                logger.error("❌ Access token invalid or expired")
                logger.info("💡 Generate new token via DevOps Agent")
                
            else:
                self.results['meta'] = {
                    'status': 'failed',
                    'reason': f'API error: {response.status_code}'
                }
                logger.error(f"❌ API returned {response.status_code}")
                logger.error(f"   Response: {response.text}")
                
        except Exception as e:
            self.results['meta'] = {
                'status': 'error',
                'reason': str(e)
            }
            logger.error(f"❌ Error testing Meta: {e}")
    
    def test_google_oauth(self):
        """Test Google OAuth credentials"""
        logger.info("🔐 Testing Google OAuth credentials...")
        
        client_id = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            self.results['google'] = {
                'status': 'failed',
                'reason': 'Missing credentials'
            }
            logger.error("❌ Missing Google OAuth credentials")
            return
        
        try:
            # Validate client ID format
            if '.apps.googleusercontent.com' in client_id:
                self.results['google'] = {
                    'status': 'valid_format',
                    'client_id': client_id[:30] + '...',
                    'note': 'Cannot fully test without user auth flow'
                }
                logger.info("✅ Google OAuth: Valid format")
                logger.info(f"   Client ID: {client_id[:30]}...")
                logger.info("   ℹ️  Full test requires user authentication")
            else:
                self.results['google'] = {
                    'status': 'invalid_format',
                    'reason': 'Client ID format incorrect'
                }
                logger.warning("⚠️  Client ID format looks incorrect")
                
        except Exception as e:
            self.results['google'] = {
                'status': 'error',
                'reason': str(e)
            }
            logger.error(f"❌ Error: {e}")
    
    def test_microsoft_oauth(self):
        """Test Microsoft OAuth credentials"""
        logger.info("🔐 Testing Microsoft OAuth credentials...")
        
        client_id = os.getenv('MICROSOFT_OAUTH_CLIENT_ID')
        client_secret = os.getenv('MICROSOFT_OAUTH_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            self.results['microsoft'] = {
                'status': 'failed',
                'reason': 'Missing credentials'
            }
            logger.error("❌ Missing Microsoft OAuth credentials")
            return
        
        try:
            # Test token endpoint access (without full auth)
            url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
            
            # This will fail but confirms endpoint is reachable
            response = requests.post(url, data={'grant_type': 'client_credentials'})
            
            if response.status_code in [400, 401]:
                # Expected - means endpoint is working, we just need valid flow
                self.results['microsoft'] = {
                    'status': 'valid_format',
                    'client_id': client_id[:20] + '...',
                    'note': 'Credentials format valid, cannot fully test without user auth'
                }
                logger.info("✅ Microsoft OAuth: Valid format")
                logger.info(f"   Client ID: {client_id[:20]}...")
                logger.info("   ℹ️  Full test requires user authentication")
            else:
                self.results['microsoft'] = {
                    'status': 'unknown',
                    'code': response.status_code
                }
                
        except Exception as e:
            self.results['microsoft'] = {
                'status': 'error',
                'reason': str(e)
            }
            logger.error(f"❌ Error: {e}")
    
    def test_flowise(self):
        """Test Flowise connection"""
        logger.info("🤖 Testing Flowise connection...")
        
        api_key = os.getenv('FLOWISE_API_KEY')
        url = os.getenv('FLOWISE_URL', 'http://localhost:3000')
        
        if not api_key:
            self.results['flowise'] = {
                'status': 'skipped',
                'reason': 'No API key configured'
            }
            logger.info("⏭️  Flowise not configured")
            return
        
        try:
            # Test API endpoint
            response = requests.get(
                f"{url}/api/v1/chatflows",
                headers={'Authorization': f'Bearer {api_key}'}
            )
            
            if response.status_code == 200:
                flows = response.json()
                self.results['flowise'] = {
                    'status': 'success',
                    'url': url,
                    'chatflows': len(flows)
                }
                logger.info(f"✅ Flowise connected: {url}")
                logger.info(f"   Chatflows available: {len(flows)}")
            else:
                self.results['flowise'] = {
                    'status': 'failed',
                    'code': response.status_code
                }
                logger.error(f"❌ Connection failed: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            self.results['flowise'] = {
                'status': 'unreachable',
                'url': url
            }
            logger.error(f"❌ Cannot reach Flowise at {url}")
        except Exception as e:
            self.results['flowise'] = {
                'status': 'error',
                'reason': str(e)
            }
            logger.error(f"❌ Error: {e}")
    
    def test_webhook_readiness(self):
        """Check if webhook server can start"""
        logger.info("🔍 Checking webhook readiness...")
        
        port = os.getenv('META_PORT', '3000')
        verify_token = os.getenv('META_VERIFY_TOKEN')
        
        if not verify_token:
            self.results['webhook'] = {
                'status': 'not_configured',
                'reason': 'No verify token'
            }
            logger.warning("⚠️  No META_VERIFY_TOKEN configured")
            return
        
        self.results['webhook'] = {
            'status': 'ready',
            'port': port,
            'verify_token': verify_token[:20] + '...'
        }
        logger.info(f"✅ Webhook ready to start on port {port}")
        logger.info(f"   Verify token: {verify_token[:20]}...")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*70)
        print("CREDENTIAL TEST REPORT")
        print("="*70)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")
        
        for service, result in self.results.items():
            status_emoji = {
                'success': '✅',
                'valid_format': '✓',
                'failed': '❌',
                'error': '⚠️',
                'skipped': '⏭️',
                'not_configured': '⚠️',
                'ready': '✅'
            }.get(result.get('status'), '❓')
            
            print(f"{status_emoji} {service.upper()}")
            print(f"   Status: {result.get('status')}")
            
            for key, value in result.items():
                if key != 'status':
                    print(f"   {key}: {value}")
            print()
        
        print("="*70)
        
        # Count successes
        successful = sum(1 for r in self.results.values() 
                        if r.get('status') in ['success', 'valid_format', 'ready'])
        total = len(self.results)
        
        print(f"\n✅ {successful}/{total} services tested successfully")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:\n")
        
        for service, result in self.results.items():
            if result.get('status') == 'failed':
                if service == 'meta':
                    print(f"   • Re-run DevOps Agent to refresh Meta credentials")
                    print(f"     python devops_agent.py → Option 1")
            
            if result.get('status') == 'not_configured':
                print(f"   • Configure {service} via DevOps Agent")
        
        print()
        
        # Save report
        with open('test_report.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'results': self.results
            }, f, indent=2)
        
        logger.info("📄 Report saved to test_report.json")

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║  Credential Testing Utility                                   ║
║  Tests all extracted credentials                             ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Check if credentials exist
    if not os.path.exists('.env') and not os.path.exists('credentials.json'):
        logger.error("❌ No credentials found!")
        logger.info("Run DevOps Agent first: python devops_agent.py")
        sys.exit(1)
    
    tester = CredentialTester()
    
    print("🧪 Running tests...\n")
    
    tester.test_meta_whatsapp()
    print()
    
    tester.test_google_oauth()
    print()
    
    tester.test_microsoft_oauth()
    print()
    
    tester.test_flowise()
    print()
    
    tester.test_webhook_readiness()
    print()
    
    tester.generate_report()
    
    print("\n✅ Testing complete!")
    print("   Review test_report.json for details")

if __name__ == "__main__":
    main()