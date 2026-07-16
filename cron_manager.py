#!/usr/bin/env python3
"""
Cron Job Manager for Instagram Reels Scraper
- Schedule automatic reels scraping
- Auto-save to repo
- Git commit & push
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import schedule
import logging
from loguru import logger

# Setup logging
LOGS_DIR = Path.home() / "Downloads" / "instagram_reels" / "cron_logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

log_file = LOGS_DIR / f"cron_job_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logger.add(str(log_file), rotation="500 MB", retention="7 days")
logger.add(sys.stdout, format="<level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>")


# ============================================================================
# Configuration
# ============================================================================

class CronConfig:
    """Cron job configuration"""
    
    # Git repository configuration
    REPO_PATH = Path.home() / "projects" / "sai"  # Local clone of rrrr666w4/sai
    REPO_URL = "https://github.com/rrrr666w4/sai"
    REPO_BRANCH = "main"
    
    # Reels scraper configuration
    REELS_SOURCE_DIR = Path.home() / "Downloads" / "instagram_reels"
    REELS_DEST_DIR = REPO_PATH / "scraped_reels"
    
    # Cron schedule (examples: "09:00", "14:30", every 6 hours, etc.)
    CRON_SCHEDULE = "09:00"  # Daily at 9 AM
    INTERVAL_HOURS = 6  # Or run every 6 hours
    USE_INTERVAL = False  # Set True for interval-based scheduling
    
    # Git commit settings
    GIT_USER_NAME = "rrrr666w4"
    GIT_USER_EMAIL = "dedsecbigra@outlook.com"
    AUTO_COMMIT = True
    AUTO_PUSH = True


# ============================================================================
# Cron Job Manager
# ============================================================================

class ReelsScraperCronManager:
    """Manage cron jobs for reels scraping"""
    
    def __init__(self):
        self.logger = logger.bind(module="cron-manager")
        self.config = CronConfig()
        self.logger.info("✅ Cron Manager initialized")
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration and setup"""
        try:
            # Check if repo exists, if not clone it
            if not self.config.REPO_PATH.exists():
                self.logger.info(f"📁 Cloning repository from {self.config.REPO_URL}")
                subprocess.run(
                    ["git", "clone", self.config.REPO_URL, str(self.config.REPO_PATH)],
                    check=True,
                    capture_output=True
                )
                self.logger.info("✅ Repository cloned successfully")
            
            # Create destination directory
            self.config.REELS_DEST_DIR.mkdir(parents=True, exist_ok=True)
            
            # Configure git user
            self._configure_git()
            
            self.logger.info("✅ Configuration validated")
            
        except Exception as e:
            self.logger.error(f"❌ Configuration validation failed: {e}")
            raise
    
    def _configure_git(self):
        """Configure git with user details"""
        try:
            os.chdir(self.config.REPO_PATH)
            
            subprocess.run(
                ["git", "config", "user.name", self.config.GIT_USER_NAME],
                check=True,
                capture_output=True
            )
            subprocess.run(
                ["git", "config", "user.email", self.config.GIT_USER_EMAIL],
                check=True,
                capture_output=True
            )
            
            self.logger.info("✅ Git configured")
        except Exception as e:
            self.logger.error(f"❌ Git configuration failed: {e}")
    
    # ────────────────────────────────────────────────────────────────────
    # Sync Operations
    # ────────────────────────────────────────────────────────────────────
    
    def sync_reels_to_repo(self):
        """
        Sync scraped reels from source to repository
        """
        try:
            self.logger.info("🔄 Starting reels sync to repository...")
            
            # Check if source has new files
            if not self.config.REELS_SOURCE_DIR.exists():
                self.logger.warning(f"⚠️ Source directory not found: {self.config.REELS_SOURCE_DIR}")
                return False
            
            # Copy metadata files
            metadata_src = self.config.REELS_SOURCE_DIR / "metadata"
            metadata_dest = self.config.REELS_DEST_DIR / "metadata"
            
            if metadata_src.exists():
                self._copy_directory(metadata_src, metadata_dest)
                self.logger.info(f"✅ Metadata synced to {metadata_dest}")
            
            # Copy videos directory (if exists and not too large)
            videos_src = self.config.REELS_SOURCE_DIR / "videos"
            videos_dest = self.config.REELS_DEST_DIR / "videos"
            
            if videos_src.exists():
                # Check total size before copying
                total_size = self._get_directory_size(videos_src)
                max_size_mb = 1000  # 1GB limit
                
                if total_size / (1024 * 1024) > max_size_mb:
                    self.logger.warning(
                        f"⚠️ Videos directory too large ({total_size / (1024*1024):.2f}MB). "
                        f"Only copying recent videos."
                    )
                    self._copy_recent_files(videos_src, videos_dest, max_size_mb)
                else:
                    self._copy_directory(videos_src, videos_dest)
                    self.logger.info(f"✅ Videos synced to {videos_dest}")
            
            # Copy logs
            logs_src = self.config.REELS_SOURCE_DIR / "logs"
            logs_dest = self.config.REELS_DEST_DIR / "logs"
            
            if logs_src.exists():
                self._copy_directory(logs_src, logs_dest)
                self.logger.info(f"✅ Logs synced to {logs_dest}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error syncing reels: {e}")
            return False
    
    def commit_and_push(self) -> bool:
        """
        Commit changes to git and push to remote
        """
        try:
            os.chdir(self.config.REPO_PATH)
            
            # Pull latest changes
            self.logger.info("📥 Pulling latest changes...")
            subprocess.run(
                ["git", "pull", "origin", self.config.REPO_BRANCH],
                check=True,
                capture_output=True
            )
            
            # Add all changes
            self.logger.info("📝 Adding files to git...")
            subprocess.run(
                ["git", "add", "-A"],
                check=True,
                capture_output=True
            )
            
            # Check if there are changes to commit
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True
            )
            
            if not result.stdout.strip():
                self.logger.info("ℹ️ No changes to commit")
                return True
            
            # Create commit message
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_message = f"🎬 Auto-sync reels metadata - {timestamp}"
            
            # Commit
            self.logger.info(f"💾 Committing: {commit_message}")
            subprocess.run(
                ["git", "commit", "-m", commit_message],
                check=True,
                capture_output=True
            )
            
            # Push
            if self.config.AUTO_PUSH:
                self.logger.info("🚀 Pushing to remote...")
                subprocess.run(
                    ["git", "push", "origin", self.config.REPO_BRANCH],
                    check=True,
                    capture_output=True
                )
                self.logger.info("✅ Changes pushed to remote")
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Git operation failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Error in commit and push: {e}")
            return False
    
    # ────────────────────────────────────────────────────────────────────
    # Scheduled Job
    # ────────────────────────────────────────────────────────────────────
    
    def scheduled_job(self):
        """
        Main scheduled job that runs at specified intervals
        """
        try:
            self.logger.info("🔔 Cron job triggered")
            
            # Sync reels
            sync_success = self.sync_reels_to_repo()
            if not sync_success:
                self.logger.warning("⚠️ Sync failed, skipping commit")
                return
            
            # Commit and push
            if self.config.AUTO_COMMIT:
                commit_success = self.commit_and_push()
                if commit_success:
                    self.logger.info("✅ Cron job completed successfully")
                else:
                    self.logger.error("❌ Commit/push failed")
            
            # Log statistics
            self._log_statistics()
            
        except Exception as e:
            self.logger.error(f"❌ Cron job failed: {e}")
    
    def _log_statistics(self):
        """Log sync statistics"""
        try:
            if self.config.REELS_DEST_DIR.exists():
                metadata_files = list((self.config.REELS_DEST_DIR / "metadata").glob("*.csv"))
                video_files = list((self.config.REELS_DEST_DIR / "videos").glob("*.mp4"))
                
                self.logger.info(f"📊 Current stats:")
                self.logger.info(f"   - Metadata files: {len(metadata_files)}")
                self.logger.info(f"   - Videos: {len(video_files)}")
        except Exception as e:
            self.logger.debug(f"Could not log statistics: {e}")
    
    # ────────────────────────────────────────────────────────────────────
    # Utility Methods
    # ────────────────────────────────────────────────────────────────────
    
    def _copy_directory(self, src: Path, dest: Path):
        """Copy directory recursively"""
        try:
            dest.mkdir(parents=True, exist_ok=True)
            
            for item in src.rglob("*"):
                if item.is_file():
                    relative_path = item.relative_to(src)
                    dest_file = dest / relative_path
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Only copy if source is newer
                    if not dest_file.exists() or item.stat().st_mtime > dest_file.stat().st_mtime:
                        import shutil
                        shutil.copy2(item, dest_file)
        except Exception as e:
            self.logger.error(f"❌ Error copying directory: {e}")
    
    def _copy_recent_files(self, src: Path, dest: Path, max_size_mb: float):
        """Copy only recent files up to size limit"""
        try:
            import shutil
            dest.mkdir(parents=True, exist_ok=True)
            
            files = sorted(src.glob("**/*"), key=lambda p: p.stat().st_mtime, reverse=True)
            total_size = 0
            
            for file in files:
                if file.is_file():
                    file_size = file.stat().st_size
                    
                    if total_size + file_size > max_size_mb * 1024 * 1024:
                        break
                    
                    relative_path = file.relative_to(src)
                    dest_file = dest / relative_path
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    shutil.copy2(file, dest_file)
                    total_size += file_size
        except Exception as e:
            self.logger.error(f"❌ Error copying recent files: {e}")
    
    def _get_directory_size(self, path: Path) -> int:
        """Get total size of directory in bytes"""
        total = 0
        for entry in path.rglob("*"):
            if entry.is_file():
                total += entry.stat().st_size
        return total
    
    # ────────────────────────────────────────────────────────────────────
    # Scheduler Management
    # ────────────────────────────────────────────────────────────────────
    
    def start_scheduler(self):
        """Start the job scheduler"""
        try:
            self.logger.info("⏰ Starting cron job scheduler...")
            
            if self.config.USE_INTERVAL:
                # Interval-based scheduling
                schedule.every(self.config.INTERVAL_HOURS).hours.do(self.scheduled_job)
                self.logger.info(f"📅 Scheduled to run every {self.config.INTERVAL_HOURS} hour(s)")
            else:
                # Time-based scheduling
                schedule.every().day.at(self.config.CRON_SCHEDULE).do(self.scheduled_job)
                self.logger.info(f"📅 Scheduled to run daily at {self.config.CRON_SCHEDULE}")
            
            # Also run once at startup
            self.logger.info("🚀 Running initial job...")
            self.scheduled_job()
            
            # Keep scheduler running
            self.logger.info("✅ Scheduler started. Press Ctrl+C to stop.")
            
            while True:
                schedule.run_pending()
                time.sleep(60)
            
        except KeyboardInterrupt:
            self.logger.info("🛑 Scheduler stopped by user")
        except Exception as e:
            self.logger.error(f"❌ Scheduler error: {e}")
    
    def run_once(self):
        """Run the job once without scheduling"""
        self.logger.info("▶️ Running job once...")
        self.scheduled_job()
        self.logger.info("✅ Job completed")


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Instagram Reels Scraper Cron Manager")
    parser.add_argument(
        "--action",
        choices=["start", "sync", "commit", "test"],
        default="start",
        help="Action to perform"
    )
    parser.add_argument(
        "--config",
        help="Path to custom config file (JSON)"
    )
    
    args = parser.parse_args()
    
    # Create manager
    manager = ReelsScraperCronManager()
    
    if args.action == "start":
        # Start the scheduler
        manager.start_scheduler()
    
    elif args.action == "sync":
        # Run sync only
        logger.info("🔄 Running sync only...")
        manager.sync_reels_to_repo()
    
    elif args.action == "commit":
        # Run commit/push only
        logger.info("💾 Running commit/push only...")
        manager.commit_and_push()
    
    elif args.action == "test":
        # Test configuration
        logger.info("✅ Configuration test successful!")
        logger.info(f"   Repository: {manager.config.REPO_PATH}")
        logger.info(f"   Source: {manager.config.REELS_SOURCE_DIR}")
        logger.info(f"   Destination: {manager.config.REELS_DEST_DIR}")


if __name__ == "__main__":
    main()
