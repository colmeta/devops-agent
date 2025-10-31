"""
Lead Scraper & Client Finder
Finds potential clients who need chatbot services
"""

import asyncio
import json
import logging
from playwright.async_api import async_playwright, Page
from typing import List, Dict, Optional
import csv
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LeadScraper:
    """Scrapes and finds potential clients for chatbot services"""
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.browser = None
        self.context = None
        self.playwright = None
        self.leads = []
    
    async def start(self):
        """Initialize browser"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        logger.info("🚀 Browser started for lead scraping")
    
    async def stop(self):
        """Cleanup"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("👋 Browser closed")
    
    async def scrape_linkedin_leads(self, search_query: str, max_results: int = 50) -> List[Dict]:
        """
        Scrape LinkedIn for potential leads
        Example search: "customer service manager" OR "business owner"
        """
        page = await self.context.new_page()
        leads = []
        
        try:
            logger.info(f"🔍 Searching LinkedIn for: {search_query}")
            
            # Login required - user must provide credentials
            linkedin_email = os.getenv('LINKEDIN_EMAIL')
            linkedin_password = os.getenv('LINKEDIN_PASSWORD')
            
            if not linkedin_email or not linkedin_password:
                logger.error("❌ LinkedIn credentials not set")
                return []
            
            # Login
            await page.goto("https://www.linkedin.com/login")
            await page.fill('input[name="session_key"]', linkedin_email)
            await page.fill('input[name="session_password"]', linkedin_password)
            await page.click('button[type="submit"]')
            await asyncio.sleep(3)
            
            # Search for leads
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={search_query}"
            await page.goto(search_url)
            await asyncio.sleep(3)
            
            # Scroll to load more results
            for _ in range(3):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)
            
            # Extract profile information
            profiles = await page.locator('.entity-result').all()
            
            for profile in profiles[:max_results]:
                try:
                    name = await profile.locator('.entity-result__title-text').inner_text()
                    headline = await profile.locator('.entity-result__primary-subtitle').inner_text()
                    location = await profile.locator('.entity-result__secondary-subtitle').inner_text()
                    profile_url = await profile.locator('a.app-aware-link').get_attribute('href')
                    
                    lead = {
                        'name': name.strip(),
                        'headline': headline.strip(),
                        'location': location.strip(),
                        'profile_url': profile_url,
                        'platform': 'linkedin',
                        'found_date': datetime.now().isoformat()
                    }
                    
                    leads.append(lead)
                    logger.info(f"✅ Found: {lead['name']} - {lead['headline']}")
                
                except Exception as e:
                    logger.warning(f"⚠️  Error extracting profile: {e}")
                    continue
            
            logger.info(f"📊 Found {len(leads)} LinkedIn leads")
            
        except Exception as e:
            logger.error(f"❌ LinkedIn scraping error: {e}")
        finally:
            await page.close()
        
        self.leads.extend(leads)
        return leads
    
    async def scrape_twitter_leads(self, hashtag: str, max_results: int = 50) -> List[Dict]:
        """
        Scrape Twitter for leads using relevant hashtags
        Example: #smallbusiness, #customerservice, #ecommerce
        """
        page = await self.context.new_page()
        leads = []
        
        try:
            logger.info(f"🐦 Searching Twitter for: {hashtag}")
            
            search_url = f"https://twitter.com/search?q={hashtag}&f=live"
            await page.goto(search_url)
            await asyncio.sleep(3)
            
            # Scroll to load tweets
            for _ in range(5):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)
            
            # Extract tweet information
            tweets = await page.locator('[data-testid="tweet"]').all()
            
            for tweet in tweets[:max_results]:
                try:
                    username = await tweet.locator('[data-testid="User-Name"]').inner_text()
                    text = await tweet.locator('[data-testid="tweetText"]').inner_text()
                    
                    # Extract @ handle
                    handle_match = username.split('\n')[1] if '\n' in username else ''
                    
                    lead = {
                        'name': username.split('\n')[0] if '\n' in username else username,
                        'handle': handle_match,
                        'tweet_text': text.strip()[:200],
                        'platform': 'twitter',
                        'hashtag': hashtag,
                        'found_date': datetime.now().isoformat()
                    }
                    
                    leads.append(lead)
                    logger.info(f"✅ Found: {lead['handle']}")
                
                except Exception as e:
                    logger.warning(f"⚠️  Error extracting tweet: {e}")
                    continue
            
            logger.info(f"📊 Found {len(leads)} Twitter leads")
            
        except Exception as e:
            logger.error(f"❌ Twitter scraping error: {e}")
        finally:
            await page.close()
        
        self.leads.extend(leads)
        return leads
    
    async def scrape_facebook_groups(self, group_url: str) -> List[Dict]:
        """
        Scrape Facebook groups for potential leads
        User must be member of the group
        """
        page = await self.context.new_page()
        leads = []
        
        try:
            logger.info(f"📘 Scraping Facebook group...")
            
            await page.goto(group_url)
            await asyncio.sleep(5)
            
            # Scroll to load posts
            for _ in range(3):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)
            
            # Extract post information
            posts = await page.locator('[data-testid="post"]').all()
            
            for post in posts[:30]:
                try:
                    author = await post.locator('[data-ad-comet-preview="message"]').inner_text()
                    post_text = await post.locator('[data-ad-comet-preview="message"]').inner_text()
                    
                    lead = {
                        'author': author[:100],
                        'post_preview': post_text[:200],
                        'platform': 'facebook',
                        'group_url': group_url,
                        'found_date': datetime.now().isoformat()
                    }
                    
                    leads.append(lead)
                    logger.info(f"✅ Found post from: {lead['author'][:30]}...")
                
                except Exception as e:
                    logger.warning(f"⚠️  Error extracting post: {e}")
                    continue
            
            logger.info(f"📊 Found {len(leads)} Facebook leads")
            
        except Exception as e:
            logger.error(f"❌ Facebook scraping error: {e}")
        finally:
            await page.close()
        
        self.leads.extend(leads)
        return leads
    
    async def scrape_google_maps_businesses(self, query: str, location: str) -> List[Dict]:
        """
        Scrape Google Maps for local businesses
        Example: "restaurants in Kampala" or "salons in Uganda"
        """
        page = await self.context.new_page()
        leads = []
        
        try:
            logger.info(f"🗺️ Searching Google Maps: {query} in {location}")
            
            search_query = f"{query} {location}".replace(' ', '+')
            await page.goto(f"https://www.google.com/maps/search/{search_query}")
            await asyncio.sleep(5)
            
            # Scroll results panel
            results_panel = await page.locator('[role="feed"]').first
            for _ in range(5):
                await results_panel.evaluate("el => el.scrollBy(0, 1000)")
                await asyncio.sleep(2)
            
            # Extract business information
            businesses = await page.locator('[role="article"]').all()
            
            for business in businesses[:50]:
                try:
                    name = await business.locator('.fontHeadlineSmall').inner_text()
                    
                    # Try to get rating and reviews
                    try:
                        rating = await business.locator('[role="img"]').get_attribute('aria-label')
                    except:
                        rating = "No rating"
                    
                    # Try to get address
                    try:
                        address_elements = await business.locator('.fontBodyMedium').all()
                        address = await address_elements[0].inner_text() if address_elements else "No address"
                    except:
                        address = "No address"
                    
                    lead = {
                        'business_name': name.strip(),
                        'rating': rating,
                        'address': address,
                        'search_query': query,
                        'location': location,
                        'platform': 'google_maps',
                        'found_date': datetime.now().isoformat()
                    }
                    
                    leads.append(lead)
                    logger.info(f"✅ Found: {lead['business_name']}")
                
                except Exception as e:
                    logger.warning(f"⚠️  Error extracting business: {e}")
                    continue
            
            logger.info(f"📊 Found {len(leads)} Google Maps leads")
            
        except Exception as e:
            logger.error(f"❌ Google Maps scraping error: {e}")
        finally:
            await page.close()
        
        self.leads.extend(leads)
        return leads
    
    def save_leads_to_csv(self, filename: str = None):
        """Save scraped leads to CSV file"""
        if not filename:
            filename = f"leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        if not self.leads:
            logger.warning("⚠️  No leads to save")
            return
        
        try:
            # Get all unique keys from all leads
            fieldnames = set()
            for lead in self.leads:
                fieldnames.update(lead.keys())
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=sorted(fieldnames))
                writer.writeheader()
                writer.writerows(self.leads)
            
            logger.info(f"✅ Saved {len(self.leads)} leads to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"❌ Error saving leads: {e}")
            return None
    
    def generate_outreach_message(self, lead: Dict, template: str = "default") -> str:
        """Generate personalized outreach message"""
        
        templates = {
            'default': """Hi {name},

I noticed your profile and thought you might be interested in our AI chatbot services. 

We help businesses like yours:
- Automate customer support 24/7
- Increase response time by 90%
- Reduce support costs by 60%

Would you be open to a quick 15-minute call to see how we can help your business?

Best regards,
Your Name""",
            
            'linkedin': """Hi {name},

I came across your profile and was impressed by your role as {headline}.

I specialize in building AI-powered chatbots that help businesses automate customer service and lead generation. Given your experience in {headline}, I thought this might be valuable for you or your network.

Would you be interested in learning more?

Best,
Your Name""",
            
            'twitter': """Hi {handle},

Saw your tweet about {topic}. We've helped similar businesses automate their customer service with AI chatbots.

Would love to show you how it works. DM me if interested! 🤖""",
            
            'cold_email': """Subject: Automate Your Customer Service with AI

Hi {name},

I help businesses automate repetitive customer inquiries using AI chatbots. Here's what we can do for you:

✅ 24/7 instant responses
✅ Handle 1000+ conversations simultaneously  
✅ Integrate with WhatsApp, Facebook, Instagram
✅ Reduce support costs by 60%

Interested in a free demo?

Reply if you'd like to see it in action!

Best regards,
Your Name
"""
        }
        
        template_text = templates.get(template, templates['default'])
        
        # Fill in placeholders
        message = template_text.format(
            name=lead.get('name', 'there'),
            headline=lead.get('headline', 'your field'),
            handle=lead.get('handle', lead.get('name', 'there')),
            topic=lead.get('hashtag', 'business automation')
        )
        
        return message
    
    def filter_quality_leads(self, keywords: List[str]) -> List[Dict]:
        """Filter leads based on quality indicators"""
        quality_leads = []
        
        for lead in self.leads:
            # Check if lead matches quality keywords
            lead_text = ' '.join(str(v).lower() for v in lead.values())
            
            if any(keyword.lower() in lead_text for keyword in keywords):
                lead['match_score'] = sum(
                    keyword.lower() in lead_text for keyword in keywords
                )
                quality_leads.append(lead)
        
        # Sort by match score
        quality_leads.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        logger.info(f"✅ Filtered to {len(quality_leads)} quality leads")
        return quality_leads

# Example usage
async def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║  Lead Scraper & Client Finder                                ║
║  Find potential clients for your chatbot services            ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    scraper = LeadScraper()
    await scraper.start()
    
    print("\n🎯 What would you like to do?")
    print("1. Scrape LinkedIn leads")
    print("2. Scrape Twitter leads")
    print("3. Scrape Google Maps businesses")
    print("4. Filter quality leads")
    print("5. Generate outreach messages")
    print("6. Save leads to CSV")
    
    choice = input("\nEnter choice (1-6): ").strip()
    
    if choice == "1":
        query = input("Enter search query (e.g., 'customer service manager'): ")
        leads = await scraper.scrape_linkedin_leads(query, max_results=50)
        print(f"\n✅ Found {len(leads)} leads!")
    
    elif choice == "2":
        hashtag = input("Enter hashtag (e.g., '#smallbusiness'): ")
        leads = await scraper.scrape_twitter_leads(hashtag, max_results=50)
        print(f"\n✅ Found {len(leads)} leads!")
    
    elif choice == "3":
        query = input("Enter business type (e.g., 'restaurants'): ")
        location = input("Enter location (e.g., 'Kampala, Uganda'): ")
        leads = await scraper.scrape_google_maps_businesses(query, location)
        print(f"\n✅ Found {len(leads)} leads!")
    
    elif choice == "4":
        keywords = input("Enter keywords (comma-separated): ").split(',')
        quality_leads = scraper.filter_quality_leads([k.strip() for k in keywords])
        print(f"\n✅ Filtered to {len(quality_leads)} quality leads!")
    
    elif choice == "5":
        if not scraper.leads:
            print("❌ No leads found. Scrape some first!")
        else:
            lead = scraper.leads[0]
            template = input("Template (default/linkedin/twitter/cold_email): ") or "default"
            message = scraper.generate_outreach_message(lead, template)
            print(f"\n📧 Generated message:\n\n{message}")
    
    elif choice == "6":
        filename = scraper.save_leads_to_csv()
        print(f"\n✅ Leads saved to {filename}")
    
    await scraper.stop()

if __name__ == "__main__":
    asyncio.run(main())