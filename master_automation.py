"""
Master Automation Controller
Integrates all automation systems: DevOps, Social Media, Lead Gen, GitHub
"""

import asyncio
import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Import all modules (ensure they're in same directory)
try:
    from devops_agent import AutomationAgent, CredentialVault
    from social_media_automation import SocialMediaAutomation
    from lead_scraper import LeadScraper
    from github_auto_push import GitHubAutoPush
except ImportError as e:
    print(f"⚠️  Import error: {e}")
    print("Make sure all modules are in the same directory")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('master_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MasterAutomation:
    """Master controller for all automation systems"""
    
    def __init__(self):
        self.devops_agent = None
        self.social_media = None
        self.lead_scraper = None
        self.github = GitHubAutoPush()
        self.config = self.load_config()
    
    def load_config(self) -> dict:
        """Load configuration from config.json"""
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                return json.load(f)
        return {}
    
    def save_config(self):
        """Save configuration"""
        with open('config.json', 'w') as f:
            json.dump(self.config, f, indent=2)
    
    # ==================
    # WORKFLOW 1: Setup Everything
    # ==================
    
    async def setup_all_credentials(self):
        """Setup all API credentials using DevOps Agent"""
        logger.info("🚀 Starting complete credential setup...")
        
        self.devops_agent = AutomationAgent(headless=False)
        await self.devops_agent.start()
        
        try:
            print("""
╔══════════════════════════════════════════════════════════════╗
║  COMPLETE SETUP WIZARD                                        ║
╚══════════════════════════════════════════════════════════════╝

This will setup:
1. Meta WhatsApp Business API
2. Google Sign-In (OAuth)
3. Microsoft Sign-In (OAuth)
4. Generate requirements.txt
5. Export .env file
6. Push to GitHub

Ready to start? (y/n): """)
            
            if input().lower() != 'y':
                return
            
            # 1. Meta WhatsApp
            print("\n📱 Step 1: Meta WhatsApp Setup")
            email = input("Facebook email: ")
            password = input("Facebook password: ")
            await self.devops_agent.setup_meta_whatsapp(email, password)
            
            # 2. Google OAuth
            print("\n🔐 Step 2: Google OAuth Setup")
            project = input("Google Cloud project name: ")
            await self.devops_agent.setup_google_oauth(project)
            
            # 3. Microsoft OAuth
            print("\n🔐 Step 3: Microsoft OAuth Setup")
            await self.devops_agent.setup_microsoft_oauth()
            
            # 4. Generate requirements.txt
            print("\n📦 Step 4: Generating requirements.txt...")
            self.devops_agent.generate_requirements_txt()
            
            # 5. Export .env
            print("\n📄 Step 5: Exporting .env...")
            env_content = self.devops_agent.vault.get_env_format()
            with open('.env', 'w') as f:
                f.write(env_content)
            
            # 6. Push to GitHub
            print("\n📤 Step 6: Pushing to GitHub...")
            result = self.github.commit_and_push("Complete setup: All credentials configured")
            
            if result['success']:
                self.github.verify_push()
                print("✅ Setup complete and pushed to GitHub!")
            else:
                print(f"⚠️  Push failed: {result.get('error')}")
            
        finally:
            await self.devops_agent.stop()
    
    # ==================
    # WORKFLOW 2: Content Creation & Social Media
    # ==================
    
    async def create_and_post_content(self, topic: str):
        """Create content and post to all social media"""
        logger.info(f"📝 Creating content about: {topic}")
        
        # Generate content (you can integrate with CrewAI here)
        content = self.generate_content(topic)
        
        # Post to social media
        self.social_media = SocialMediaAutomation()
        await self.social_media.start()
        
        try:
            results = await self.social_media.post_to_all_platforms(content)
            
            print("\n📊 Posting Results:")
            for platform, result in results.items():
                status = "✅" if result.get('success') else "❌"
                print(f"{status} {platform}: {result}")
            
            # Log results
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'topic': topic,
                'results': results
            }
            
            self.log_activity('social_media_posts', log_entry)
            
            # Push log to GitHub
            self.github.commit_and_push(f"Posted content: {topic}")
            
        finally:
            await self.social_media.stop()
    
    def generate_content(self, topic: str) -> dict:
        """Generate content for different platforms"""
        # This is a placeholder - integrate with your CrewAI system
        # or use the content generated by your crew
        
        base_content = f"""🤖 Exciting Update!

We're revolutionizing {topic} with AI-powered automation. 

✨ Key benefits:
• 24/7 availability
• Instant responses
• Reduced costs
• Better customer satisfaction

Want to learn more? DM us! 

#AI #Automation #{topic.replace(' ', '')}"""
        
        return {
            'twitter': {'content': base_content[:280]},
            'linkedin': {'content': base_content},
            'facebook': {'message': base_content},
            'medium': {
                'title': f"The Future of {topic}: AI Automation",
                'content': f"{base_content}\n\n[Full article content here]",
                'tags': ['AI', 'Automation', topic]
            }
        }
    
    # ==================
    # WORKFLOW 3: Lead Generation
    # ==================
    
    async def find_and_contact_leads(self, search_params: dict):
        """Find leads and prepare outreach"""
        logger.info("🎯 Starting lead generation...")
        
        self.lead_scraper = LeadScraper()
        await self.lead_scraper.start()
        
        try:
            all_leads = []
            
            # LinkedIn
            if search_params.get('linkedin_query'):
                leads = await self.lead_scraper.scrape_linkedin_leads(
                    search_params['linkedin_query'],
                    max_results=50
                )
                all_leads.extend(leads)
            
            # Twitter
            if search_params.get('twitter_hashtag'):
                leads = await self.lead_scraper.scrape_twitter_leads(
                    search_params['twitter_hashtag'],
                    max_results=50
                )
                all_leads.extend(leads)
            
            # Google Maps
            if search_params.get('business_type') and search_params.get('location'):
                leads = await self.lead_scraper.scrape_google_maps_businesses(
                    search_params['business_type'],
                    search_params['location']
                )
                all_leads.extend(leads)
            
            # Filter quality leads
            quality_keywords = search_params.get('quality_keywords', [
                'customer service', 'support', 'business owner', 
                'manager', 'director', 'CEO'
            ])
            
            quality_leads = self.lead_scraper.filter_quality_leads(quality_keywords)
            
            # Save to CSV
            filename = self.lead_scraper.save_leads_to_csv()
            
            # Generate outreach messages
            outreach_file = f"outreach_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(outreach_file, 'w', encoding='utf-8') as f:
                for lead in quality_leads[:20]:  # Top 20 leads
                    message = self.lead_scraper.generate_outreach_message(
                        lead,
                        template='linkedin' if lead['platform'] == 'linkedin' else 'default'
                    )
                    f.write(f"\n{'='*60}\n")
                    f.write(f"TO: {lead.get('name', lead.get('handle', 'Unknown'))}\n")
                    f.write(f"PLATFORM: {lead['platform']}\n")
                    f.write(f"{'='*60}\n\n")
                    f.write(message)
                    f.write("\n\n")
            
            print(f"\n✅ Found {len(all_leads)} total leads")
            print(f"✅ {len(quality_leads)} quality leads")
            print(f"✅ Leads saved to: {filename}")
            print(f"✅ Outreach messages saved to: {outreach_file}")
            
            # Push to GitHub
            self.github.commit_and_push(f"Lead generation: {len(quality_leads)} quality leads found")
            
        finally:
            await self.lead_scraper.stop()
    
    # ==================
    # WORKFLOW 4: Integration with CrewAI
    # ==================
    
    async def run_crewai_and_post(self, niche: str):
        """Run CrewAI content generation then post everywhere"""
        logger.info(f"🤖 Running CrewAI for niche: {niche}")
        
        print("""
This will:
1. Run your CrewAI content generation
2. Extract generated content
3. Post to all social media platforms
4. Push results to GitHub

Note: Make sure your CrewAI project is configured properly
""")
        
        # Change to CrewAI project directory if needed
        crewai_path = input("Path to CrewAI project (or press Enter if current): ").strip()
        
        if crewai_path and os.path.exists(crewai_path):
            os.chdir(crewai_path)
        
        # Run CrewAI (this assumes you have crewai installed)
        try:
            print("🚀 Running CrewAI...")
            os.system(f"crewai run")  # This will run your crew
            
            # Wait for completion
            print("⏳ Waiting for CrewAI to complete...")
            await asyncio.sleep(10)
            
            # Look for output file (typically report.md)
            if os.path.exists('report.md'):
                with open('report.md', 'r', encoding='utf-8') as f:
                    content = f.read()
                
                print("✅ CrewAI completed! Content generated.")
                
                # Post to social media
                await self.create_and_post_content(niche)
                
            else:
                print("⚠️  No output file found. Check your CrewAI configuration.")
        
        except Exception as e:
            logger.error(f"Error running CrewAI: {e}")
    
    # ==================
    # UTILITIES
    # ==================
    
    def log_activity(self, activity_type: str, data: dict):
        """Log activity to JSON file"""
        log_file = 'activity_log.json'
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append({
            'type': activity_type,
            'timestamp': datetime.now().isoformat(),
            'data': data
        })
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def show_dashboard(self):
        """Show activity dashboard"""
        if not os.path.exists('activity_log.json'):
            print("📊 No activity logged yet")
            return
        
        with open('activity_log.json', 'r') as f:
            logs = json.load(f)
        
        print("\n╔══════════════════════════════════════════════════════════════╗")
        print("║  ACTIVITY DASHBOARD                                           ║")
        print("╚══════════════════════════════════════════════════════════════╝\n")
        
        # Count by type
        from collections import Counter
        counts = Counter(log['type'] for log in logs)
        
        for activity_type, count in counts.items():
            print(f"📊 {activity_type}: {count} activities")
        
        print(f"\n📅 Total activities: {len(logs)}")
        
        if logs:
            last = logs[-1]
            print(f"🕐 Last activity: {last['type']} at {last['timestamp']}")

# Main CLI
async def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║  MASTER AUTOMATION CONTROLLER                                 ║
║  Complete Business Automation System                          ║
╚══════════════════════════════════════════════════════════════╝

What would you like to do?

1. 🔧 Complete Setup (All Credentials + GitHub)
2. 📱 Create & Post Social Media Content
3. 🎯 Find Leads & Generate Outreach
4. 🤖 Run CrewAI + Auto-Post
5. 📊 View Dashboard
6. 📤 Push Everything to GitHub
7. Exit

""")
    
    master = MasterAutomation()
    
    choice = input("Enter choice (1-7): ").strip()
    
    if choice == "1":
        await master.setup_all_credentials()
    
    elif choice == "2":
        topic = input("Content topic: ")
        await master.create_and_post_content(topic)
    
    elif choice == "3":
        search_params = {
            'linkedin_query': input("LinkedIn search query (or press Enter to skip): ") or None,
            'twitter_hashtag': input("Twitter hashtag (or press Enter to skip): ") or None,
            'business_type': input("Business type for Google Maps (or press Enter to skip): ") or None,
            'location': input("Location (or press Enter to skip): ") or None
        }
        await master.find_and_contact_leads(search_params)
    
    elif choice == "4":
        niche = input("Enter niche for CrewAI: ")
        await master.run_crewai_and_post(niche)
    
    elif choice == "5":
        master.show_dashboard()
    
    elif choice == "6":
        message = input("Commit message (or press Enter for auto): ") or None
        result = master.github.commit_and_push(message)
        print(json.dumps(result, indent=2))
    
    elif choice == "7":
        print("👋 Goodbye!")
        return
    
    print("\n✅ Operation complete!")

if __name__ == "__main__":
    asyncio.run(main())