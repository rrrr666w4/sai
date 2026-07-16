# 🎬 Instagram Reels Scraper & Auto-Sync

ہجی ایک **مکمل automation solution** ہے Instagram Reels کو scrape کرنے اور GitHub repo میں auto-sync کرنے کے لیے۔

## ✨ Features

✅ **Reels Metadata Extraction:**
- Author username
- Likes, comments, views, shares
- Caption & posted date
- Author profile info (followers)

✅ **Automated Sync:**
- Cron job based scheduling
- GitHub Actions workflow
- Auto commit & push

✅ **Multiple Formats:**
- CSV export
- JSON export
- Organized folder structure

## 📁 Directory Structure

```
rrrr666w4/sai/
├── reels_scraper.py          # Main scraper script
├── cron_manager.py           # Cron job manager
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── .github/
│   └── workflows/
│       └── scrape-reels.yml  # GitHub Actions workflow
└── scraped_reels/           # Output directory
    ├── metadata/
    │   ├── reels_metadata.csv
    │   └── reels_metadata.json
    ├── videos/
    └── logs/
```

## 🚀 Quick Start

### 1️⃣ Clone Repository

```bash
git clone https://github.com/rrrr666w4/sai.git
cd sai
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Run Scraper (Standalone)

#### Scrape single reel:
```bash
python reels_scraper.py --url "https://www.instagram.com/reel/YOUR_REEL_ID/"
```

#### Scrape hashtag reels:
```bash
python reels_scraper.py --hashtag "reels" --max-reels 20
```

### 4️⃣ Run Cron Job Manager

#### Start scheduler (runs automatically):
```bash
python cron_manager.py --action start
```

#### Run once (no scheduling):
```bash
python cron_manager.py --action sync
```

#### Test configuration:
```bash
python cron_manager.py --action test
```

## 🔄 GitHub Actions Workflow

### Manual Trigger

1. Go to **Actions** tab
2. Select **"🎬 Scrape Instagram Reels & Sync to Repo"**
3. Click **"Run workflow"**
4. Fill in inputs:
   - **Hashtag**: reels (یا کوئی اور hashtag)
   - **Max reels**: 10 (یا زیادہ)
   - **Auto-sync**: true

### Automatic Schedule

✅ Runs **daily at 9:00 AM UTC**

Edit `.github/workflows/scrape-reels.yml` میں:
```yaml
schedule:
  - cron: '0 9 * * *'  # Change time here
```

## ⚙️ Configuration

### `reels_scraper.py`

```python
# Output directories
REELS_OUTPUT_DIR = Path.home() / "Downloads" / "instagram_reels"
METADATA_DIR = REELS_OUTPUT_DIR / "metadata"
VIDEOS_DIR = REELS_OUTPUT_DIR / "videos"
```

### `cron_manager.py`

```python
class CronConfig:
    REPO_PATH = Path.home() / "projects" / "sai"
    REPO_URL = "https://github.com/rrrr666w4/sai"
    CRON_SCHEDULE = "09:00"  # Daily at 9 AM
    INTERVAL_HOURS = 6       # Or every 6 hours
    USE_INTERVAL = False
    AUTO_COMMIT = True
    AUTO_PUSH = True
```

## 📊 Output Format

### CSV Example (`reels_metadata.csv`)

```
reel_id,url,author_username,author_full_name,author_followers,caption,likes_count,comments_count,views_count,shares_count,posted_at,scraped_at
ABC123,https://www.instagram.com/reel/ABC123/,username123,User Name,50000,"Amazing video!",1250,45,25000,120,2 days ago,2026-07-16T09:00:00
```

### JSON Example (`reels_metadata.json`)

```json
[
  {
    "reel_id": "ABC123",
    "url": "https://www.instagram.com/reel/ABC123/",
    "author_username": "username123",
    "author_full_name": "User Name",
    "author_followers": 50000,
    "caption": "Amazing video!",
    "likes_count": 1250,
    "comments_count": 45,
    "views_count": 25000,
    "shares_count": 120,
    "posted_at": "2 days ago",
    "scraped_at": "2026-07-16T09:00:00"
  }
]
```

## 🔧 Setup Instructions

### Local Setup

```bash
# 1. Clone repo
git clone https://github.com/rrrr666w4/sai.git
cd sai

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure cron manager
# Edit cron_manager.py and update CronConfig

# 5. Start scheduler
python cron_manager.py --action start
```

### GitHub Actions Setup

1. **Ensure secrets are configured:**
   - `GITHUB_TOKEN` (automatically provided)
   - `GIT_USER_EMAIL` (optional)
   - `GIT_USER_NAME` (optional)

2. **Trigger workflow manually:**
   - Go to Actions tab
   - Select workflow
   - Click "Run workflow"

3. **Check results:**
   - View workflow run logs
   - Download artifacts
   - Check repository for new commits

## 📋 Requirements

```
requests>=2.31.0
rich>=13.0.0
loguru>=0.7.0
schedule>=1.2.0
uiautomator2>=2.16.0
```

Install with:
```bash
pip install -r requirements.txt
```

## 🐛 Troubleshooting

### Issue: No reels scraped

**Solution:**
- Check Android device is connected via ADB
- Verify Instagram app is installed
- Check internet connection
- Review logs in `instagram_reels/logs/`

### Issue: Git push fails

**Solution:**
- Verify `GITHUB_TOKEN` is set correctly
- Check repository permissions
- Ensure branch name is correct in config

### Issue: Cron job not running

**Solution:**
```bash
# Check if scheduler is running
ps aux | grep cron_manager.py

# View logs
tail -f ~/Downloads/instagram_reels/cron_logs/*.log

# Test once
python cron_manager.py --action test
```

## 📝 API Reference

### ReelsScraperCronManager

```python
from cron_manager import ReelsScraperCronManager

manager = ReelsScraperCronManager()

# Run job once
manager.scheduled_job()

# Sync only
manager.sync_reels_to_repo()

# Commit & push only
manager.commit_and_push()

# Start scheduler
manager.start_scheduler()
```

### InstagramReelsScraper

```python
from reels_scraper import InstagramReelsScraper
from taktik.core.shared.device.manager import DeviceManager

device_manager = DeviceManager()
device_manager.connect()

scraper = InstagramReelsScraper(device_manager)

# Scrape single reel
metadata = scraper.scrape_reel_from_url("https://www.instagram.com/reel/ABC123/")

# Scrape hashtag
results = scraper.scrape_hashtag_reels("reels", max_reels=50)

# Export
scraper.export_to_csv()
scraper.export_to_json()

# Print summary
scraper.print_summary()
```

## 🔐 Security Notes

- ✅ Use GitHub Secrets for sensitive data
- ✅ Store credentials securely
- ✅ Don't commit `.env` files
- ✅ Review logs for sensitive info

## 📞 Support

For issues, questions, or contributions:

1. **Check logs:** `~/Downloads/instagram_reels/logs/`
2. **Review README:** This file
3. **Test workflow:** Use `--action test`

## 📄 License

This project is part of **rrrr666w4/sai** repository.

---

**Last Updated:** 2026-07-16
**Version:** 1.0.0
**Author:** @rrrr666w4
