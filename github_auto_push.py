"""
GitHub Auto-Push Module
Automatically commits and pushes to GitHub with verification
"""

import os
import subprocess
import json
from datetime import datetime
import requests
from typing import Optional, Dict

class GitHubAutoPush:
    """Automates GitHub operations"""
    
    def __init__(self, username: str = "colmeta", repo: str = "clarity-pearl-production"):
        self.username = username
        self.repo = repo
        self.token = os.getenv('GITHUB_TOKEN')
        
        if not self.token:
            print("⚠️  GITHUB_TOKEN not set. Some operations may fail.")
    
    def init_repo(self) -> bool:
        """Initialize git repository if not already initialized"""
        try:
            # Check if git is installed
            result = subprocess.run(['git', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Git is not installed. Install from https://git-scm.com/")
                return False
            
            # Check if already a git repo
            result = subprocess.run(['git', 'rev-parse', '--git-dir'],
                                  capture_output=True, text=True, cwd=os.getcwd())
            
            if result.returncode == 0:
                print("✅ Git repository already initialized")
                return True
            
            # Initialize repo
            print("📦 Initializing git repository...")
            subprocess.run(['git', 'init'], check=True)
            subprocess.run(['git', 'branch', '-M', 'main'], check=True)
            
            # Add remote
            remote_url = f"https://github.com/{self.username}/{self.repo}.git"
            subprocess.run(['git', 'remote', 'add', 'origin', remote_url], 
                         check=True)
            
            print("✅ Git repository initialized")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error initializing repo: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def commit_and_push(self, message: Optional[str] = None) -> Dict:
        """Commit all changes and push to GitHub"""
        if not message:
            message = f"Auto-update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        try:
            # Check git status
            status_result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True, text=True, check=True
            )
            
            if not status_result.stdout.strip():
                return {
                    'success': True,
                    'message': 'No changes to commit',
                    'committed': False
                }
            
            # Stage all changes
            print("📦 Staging changes...")
            subprocess.run(['git', 'add', '.'], check=True)
            
            # Commit
            print(f"💾 Committing: {message}")
            subprocess.run(['git', 'commit', '-m', message], check=True)
            
            # Push
            print("🚀 Pushing to GitHub...")
            
            if self.token:
                # Use token for authentication
                remote_url = f"https://{self.token}@github.com/{self.username}/{self.repo}.git"
                subprocess.run(['git', 'remote', 'set-url', 'origin', remote_url], 
                             check=True)
            
            push_result = subprocess.run(
                ['git', 'push', '-u', 'origin', 'main'],
                capture_output=True, text=True
            )
            
            if push_result.returncode == 0:
                print("✅ Successfully pushed to GitHub!")
                return {
                    'success': True,
                    'message': 'Changes pushed successfully',
                    'committed': True,
                    'commit_message': message,
                    'repo_url': f"https://github.com/{self.username}/{self.repo}"
                }
            else:
                error_msg = push_result.stderr
                print(f"❌ Push failed: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'committed': True,
                    'pushed': False
                }
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git operation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'committed': False
            }
    
    def verify_push(self) -> bool:
        """Verify that push was successful by checking GitHub API"""
        if not self.token:
            print("⚠️  Cannot verify without GITHUB_TOKEN")
            return False
        
        try:
            headers = {
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            url = f"https://api.github.com/repos/{self.username}/{self.repo}/commits"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                commits = response.json()
                if commits:
                    latest = commits[0]
                    print(f"✅ Latest commit verified:")
                    print(f"   SHA: {latest['sha'][:7]}")
                    print(f"   Message: {latest['commit']['message']}")
                    print(f"   Date: {latest['commit']['author']['date']}")
                    return True
            else:
                print(f"⚠️  Could not verify: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"⚠️  Verification error: {e}")
            return False
    
    def get_repo_info(self) -> Dict:
        """Get repository information"""
        if not self.token:
            return {'error': 'GITHUB_TOKEN required'}
        
        try:
            headers = {
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            url = f"https://api.github.com/repos/{self.username}/{self.repo}"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'name': data['name'],
                    'description': data['description'],
                    'url': data['html_url'],
                    'stars': data['stargazers_count'],
                    'forks': data['forks_count'],
                    'default_branch': data['default_branch'],
                    'last_push': data['pushed_at']
                }
            else:
                return {'error': f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {'error': str(e)}
    
    def create_issue(self, title: str, body: str) -> bool:
        """Create a GitHub issue (useful for error reporting)"""
        if not self.token:
            print("⚠️  GITHUB_TOKEN required to create issues")
            return False
        
        try:
            headers = {
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json',
                'Content-Type': 'application/json'
            }
            
            url = f"https://api.github.com/repos/{self.username}/{self.repo}/issues"
            data = {'title': title, 'body': body}
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 201:
                issue_url = response.json()['html_url']
                print(f"✅ Issue created: {issue_url}")
                return True
            else:
                print(f"❌ Failed to create issue: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating issue: {e}")
            return False

# Integration with DevOps Agent
def auto_backup_credentials(vault_path: str = "credentials.json"):
    """Automatically backup credentials to GitHub"""
    github = GitHubAutoPush()
    
    if os.path.exists(vault_path):
        # Initialize repo
        if not github.init_repo():
            return False
        
        # Commit and push
        result = github.commit_and_push("Auto-backup: Updated credentials")
        
        if result['success']:
            # Verify push
            github.verify_push()
            return True
        else:
            return False
    else:
        print(f"⚠️  {vault_path} not found")
        return False

# Example usage
if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║  GitHub Auto-Push Tool                                        ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    github = GitHubAutoPush()
    
    print("1. Initialize repository")
    print("2. Commit and push changes")
    print("3. Verify latest push")
    print("4. Get repository info")
    print("5. Backup credentials")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == "1":
        github.init_repo()
    
    elif choice == "2":
        message = input("Commit message (or press Enter for auto): ").strip()
        result = github.commit_and_push(message if message else None)
        print(json.dumps(result, indent=2))
    
    elif choice == "3":
        github.verify_push()
    
    elif choice == "4":
        info = github.get_repo_info()
        print(json.dumps(info, indent=2))
    
    elif choice == "5":
        auto_backup_credentials()
    
    print("\n✅ Done!")