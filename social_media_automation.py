"""
Social Media Automation Module
Integrates with DevOps Agent and CrewAI for automated posting
"""

import os
import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Page
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SocialMediaAutomation:
    """Automates social media posting across platforms"""
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.browser = None
        self.context = None
        self.playwright = None
        
        # Load credentials
        self.meta_token = os.getenv('META_ACCESS_TOKEN')
        self.linkedin_email = os.getenv('LINKEDIN_EMAIL')
        self.linkedin_password = os.getenv('LINKEDIN_PASSWORD')
        self.twitter_email = os.getenv('TWITTER_EMAIL')
        self.twitter_password = os.getenv('TWITTER_PASSWORD')
    
    async def start(self):
        """Initialize browser"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        logger.info("🚀 Browser started")
    
    async def stop(self):
        """Cleanup"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("👋 Browser closed")
    
    # =======================
    # META (Facebook/Instagram) via API
    # =======================
    
    def post_to_facebook(self, message: str, image_url: Optional[str] = None) -> Dict:
        """Post to Facebook using Meta Graph API"""
        if not self.meta_token:
            return {'success': False, 'error': 'META_ACCESS_TOKEN not set'}
        
        try:
            # Get Page ID first
            url = "https://graph.facebook.com/v18.0/me/accounts"
            params = {'access_token': self.meta_token}
            response = requests.get(url, params=params)
            
            if response.status_code != 200:
                return {'success': False, 'error': 'Failed to get page access'}
            
            pages = response.json().get('data', [])
            if not pages:
                return {'success': False, 'error': 'No pages found'}
            
            page_id = pages[0]['id']
            page_token = pages[0]['access_token']
            
            # Post to page
            post_url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
            post_data = {
                'message': message,
                'access_token': page_token
            }
            
            if image_url:
                post_data['link'] = image_url
            
            response = requests.post(post_url, data=post_data)
            
            if response.status_code == 200:
                post_id = response.json().get('id')
                logger.info(f"✅ Posted to Facebook: {post_id}")
                return {
                    'success': True,
                    'platform': 'facebook',
                    'post_id': post_id,
                    'url': f"https://facebook.com/{post_id}"
                }
            else:
                return {
                    'success': False,
                    'error': response.json()
                }
        
        except Exception as e:
            logger.error(f"Facebook posting error: {e}")
            return {'success': False, 'error': str(e)}
    
    def post_to_instagram(self, image_url: str, caption: str) -> Dict:
        """Post to Instagram using Meta Graph API"""
        if not self.meta_token:
            return {'success': False, 'error': 'META_ACCESS_TOKEN not set'}
        
        try:
            # Get Instagram Business Account ID
            url = "https://graph.facebook.com/v18.0/me/accounts"
            params = {'access_token': self.meta_token, 'fields': 'instagram_business_account'}
            response = requests.get(url, params=params)
            
            pages = response.json().get('data', [])
            ig_account = None
            
            for page in pages:
                if 'instagram_business_account' in page:
                    ig_account = page['instagram_business_account']['id']
                    break
            
            if not ig_account:
                return {'success': False, 'error': 'No Instagram business account linked'}
            
            # Create media container
            container_url = f"https://graph.facebook.com/v18.0/{ig_account}/media"
            container_data = {
                'image_url': image_url,
                'caption': caption,
                'access_token': self.meta_token
            }
            
            response = requests.post(container_url, data=container_data)
            
            if response.status_code != 200:
                return {'success': False, 'error': response.json()}
            
            creation_id = response.json().get('id')
            
            # Publish media
            publish_url = f"https://graph.facebook.com/v18.0/{ig_account}/media_publish"
            publish_data = {
                'creation_id': creation_id,
                'access_token': self.meta_token
            }
            
            response = requests.post(publish_url, data=publish_data)
            
            if response.status_code == 200:
                media_id = response.json().get('id')
                logger.info(f"✅ Posted to Instagram: {media_id}")
                return {
                    'success': True,
                    'platform': 'instagram',
                    'media_id': media_id
                }
            else:
                return {'success': False, 'error': response.json()}
        
        except Exception as e:
            logger.error(f"Instagram posting error: {e}")
            return {'success': False, 'error': str(e)}
    
    # =======================
    # LINKEDIN via Browser Automation
    # =======================
    
    async def post_to_linkedin(self, content: str, image_path: Optional[str] = None) -> Dict:
        """Post to LinkedIn using browser automation"""
        if not self.linkedin_email or not self.linkedin_password:
            return {'success': False, 'error': 'LinkedIn credentials not set'}
        
        page = await self.context.new_page()
        
        try:
            logger.info("📘 Posting to LinkedIn...")
            
            # Login
            await page.goto("https://www.linkedin.com/login")
            await page.fill('input[name="session_key"]', self.linkedin_email)
            await page.fill('input[name="session_password"]', self.linkedin_password)
            await page.click('button[type="submit"]')
            
            await asyncio.sleep(3)
            
            # Navigate to feed
            await page.goto("https://www.linkedin.com/feed/")
            await asyncio.sleep(2)
            
            # Click "Start a post" button
            await page.click('button:has-text("Start a post")')
            await asyncio.sleep(1)
            
            # Type content
            editor = await page.locator('[role="textbox"]').first
            await editor.fill(content)
            
            # Upload image if provided
            if image_path and os.path.exists(image_path):
                # Click image upload button
                await page.click('button[aria-label*="image"]')
                await asyncio.sleep(1)
                
                # Upload file
                await page.set_input_files('input[type="file"]', image_path)
                await asyncio.sleep(2)
            
            # Post
            await page.click('button:has-text("Post")')
            await asyncio.sleep(3)
            
            logger.info("✅ Posted to LinkedIn")
            return {
                'success': True,
                'platform': 'linkedin',
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"LinkedIn posting error: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            await page.close()
    
    # =======================
    # TWITTER/X via Browser Automation
    # =======================
    
    async def post_to_twitter(self, content: str, image_path: Optional[str] = None) -> Dict:
        """Post to Twitter/X using browser automation"""
        if not self.twitter_email or not self.twitter_password:
            return {'success': False, 'error': 'Twitter credentials not set'}
        
        page = await self.context.new_page()
        
        try:
            logger.info("🐦 Posting to Twitter...")
            
            # Login
            await page.goto("https://twitter.com/i/flow/login")
            await asyncio.sleep(2)
            
            # Enter email
            await page.fill('input[autocomplete="username"]', self.twitter_email)
            await page.click('button:has-text("Next")')
            await asyncio.sleep(2)
            
            # Enter password
            await page.fill('input[name="password"]', self.twitter_password)
            await page.click('button[data-testid="LoginForm_Login_Button"]')
            await asyncio.sleep(3)
            
            # Click tweet button
            await page.click('a[data-testid="SideNav_NewTweet_Button"]')
            await asyncio.sleep(1)
            
            # Type content
            tweet_box = await page.locator('[data-testid="tweetTextarea_0"]').first
            await tweet_box.fill(content)
            
            # Upload image if provided
            if image_path and os.path.exists(image_path):
                await page.set_input_files('input[data-testid="fileInput"]', image_path)
                await asyncio.sleep(2)
            
            # Post tweet
            await page.click('button[data-testid="tweetButtonInline"]')
            await asyncio.sleep(3)
            
            logger.info("✅ Posted to Twitter")
            return {
                'success': True,
                'platform': 'twitter',
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Twitter posting error: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            await page.close()
    
    # =======================
    # MEDIUM via Browser Automation
    # =======================
    
    async def post_to_medium(self, title: str, content: str, tags: List[str] = None) -> Dict:
        """Post article to Medium"""
        page = await self.context.new_page()
        
        try:
            logger.info("📝 Posting to Medium...")
            
            await page.goto("https://medium.com/new-story")
            await asyncio.sleep(3)
            
            # Type title
            title_box = await page.locator('h1[data-default-value="Title"]').first
            await title_box.fill(title)
            
            # Type content
            content_box = await page.locator('[data-default-value="Tell your story..."]').first
            await content_box.fill(content)
            
            # Click publish
            await page.click('button:has-text("Publish")')
            await asyncio.sleep(2)
            
            # Add tags if provided
            if tags:
                for tag in tags[:5]:  # Medium allows max 5 tags
                    await page.fill('input[placeholder="Add a tag..."]', tag)
                    await page.press('input[placeholder="Add a tag..."]', 'Enter')
                    await asyncio.sleep(0.5)
            
            # Final publish
            await page.click('button:has-text("Publish now")')
            await asyncio.sleep(3)
            
            logger.info("✅ Posted to Medium")
            return {
                'success': True,
                'platform': 'medium',
                'title': title,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Medium posting error: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            await page.close()
    
    # =======================
    # BULK POSTING
    # =======================
    
    async def post_to_all_platforms(self, content: Dict) -> Dict:
        """Post content to all platforms"""
        results = {}
        
        # Facebook
        if content.get('facebook'):
            results['facebook'] = self.post_to_facebook(
                content['facebook'].get('message', ''),
                content['facebook'].get('image_url')
            )
        
        # Instagram
        if content.get('instagram'):
            results['instagram'] = self.post_to_instagram(
                content['instagram'].get('image_url', ''),
                content['instagram'].get('caption', '')
            )
        
        # LinkedIn
        if content.get('linkedin'):
            results['linkedin'] = await self.post_to_linkedin(
                content['linkedin'].get('content', ''),
                content['linkedin'].get('image_path')
            )
        
        # Twitter
        if content.get('twitter'):
            results['twitter'] = await self.post_to_twitter(
                content['twitter'].get('content', ''),
                content['twitter'].get('image_path')
            )
        
        # Medium
        if content.get('medium'):
            results['medium'] = await self.post_to_medium(
                content['medium'].get('title', ''),
                content['medium'].get('content', ''),
                content['medium'].get('tags', [])
            )
        
        return results

# Integration with CrewAI
async def post_crew_output(output_file: str = "report.md"):
    """Post CrewAI generated content to social media"""
    if not os.path.exists(output_file):
        logger.error(f"Output file {output_file} not found")
        return
    
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse content for different platforms
    # You can customize this based on your CrewAI output format
    
    social_content = {
        'twitter': {
            'content': content[:280]  # Twitter char limit
        },
        'linkedin': {
            'content': content[:1300]  # LinkedIn char limit
        },
        'facebook': {
            'message': content[:500]
        },
        'medium': {
            'title': 'AI-Generated Content Report',
            'content': content,
            'tags': ['AI', 'Automation', 'Technology']
        }
    }
    
    automation = SocialMediaAutomation()
    await automation.start()
    
    results = await automation.post_to_all_platforms(social_content)
    
    await automation.stop()
    
    print("\n📊 Posting Results:")
    print(json.dumps(results, indent=2))

# Example usage
if __name__ == "__main__":
    asyncio.run(post_crew_output())