# GitHub Email Settings - Stop Repository Spam

## 🚫 Quick Fix: Disable Repository Notifications

### Method 1: GitHub Web Interface (Recommended)

1. **Go to your repository**: https://github.com/sandraschi/advanced-memory-mcp
2. **Click "Watch" button** (top right, next to Star/Fork)
3. **Select "Ignore"** from the dropdown
4. **Or select "Custom"** and uncheck all notification types

### Method 2: GitHub Settings

1. **Go to GitHub Settings**: https://github.com/settings/notifications
2. **Under "Watching"**: Find "advanced-memory-mcp"
3. **Click "Unwatch"** or change to "Ignore"

### Method 3: Email Filters

If you want to keep some notifications but reduce spam:

1. **Gmail**: Create a filter for emails from `noreply@github.com`
2. **Outlook**: Create a rule to move GitHub emails to a folder
3. **Other email clients**: Set up similar filters

## 🔧 Repository Notification Settings

### Disable Specific Notifications

If you want to keep watching but reduce email spam:

1. **Go to repository**: https://github.com/sandraschi/advanced-memory-mcp
2. **Click "Watch" → "Custom"**
3. **Uncheck these options**:
   - [ ] Issues
   - [ ] Pull requests
   - [ ] Releases
   - [ ] Discussions
   - [ ] Actions (CI/CD notifications)
   - [ ] Security alerts

### Keep Only Important Notifications

**Recommended minimal settings**:
- [x] Releases (important updates)
- [ ] Everything else unchecked

## 📧 Email Types You're Probably Getting

### Common Spam Sources
- **CI/CD notifications**: Every push triggers workflows
- **Dependabot updates**: Weekly dependency update PRs
- **Issue/PR notifications**: Community activity
- **Security alerts**: Dependency vulnerabilities
- **Discussion notifications**: Community discussions

### How to Stop Each Type

#### Stop CI/CD Email Spam
1. **Go to repository settings**: https://github.com/sandraschi/advanced-memory-mcp/settings
2. **Click "Notifications"** in left sidebar
3. **Uncheck "Actions"** notifications

#### Stop Dependabot Spam
1. **Go to repository settings**: https://github.com/sandraschi/advanced-memory-mcp/settings
2. **Click "Security & analysis"**
3. **Disable "Dependabot alerts"** (if you don't want security emails)

#### Stop Issue/PR Spam
1. **Watch settings**: Click "Watch" → "Custom"
2. **Uncheck "Issues" and "Pull requests"**

## 🎯 Recommended Settings for Maintainers

### If You Want Minimal Notifications
```
Watch: Custom
├── Issues: ❌ (unchecked)
├── Pull requests: ❌ (unchecked)
├── Releases: ✅ (checked)
├── Discussions: ❌ (unchecked)
├── Actions: ❌ (unchecked)
└── Security alerts: ✅ (checked)
```

### If You Want No Emails At All
```
Watch: Ignore
```

## 🔍 Check Your Current Settings

### See What You're Watching
1. **Go to**: https://github.com/settings/notifications
2. **Scroll to "Watching"** section
3. **Look for "advanced-memory-mcp"**
4. **See current notification level**

### Check Email Preferences
1. **Go to**: https://github.com/settings/emails
2. **Review "Email preferences"**
3. **Uncheck unwanted notification types**

## 🛠️ Advanced: Repository-Level Settings

### Disable Notifications for Contributors
If you're getting emails from other contributors:

1. **Go to repository settings**
2. **Click "Notifications"**
3. **Uncheck "Send notifications to watchers"**

### Disable Automatic Watching
1. **Go to GitHub settings**: https://github.com/settings/notifications
2. **Under "Auto-subscription"**
3. **Uncheck "Automatically watch repositories"**

## 📱 Mobile App Settings

### GitHub Mobile App
1. **Open GitHub app**
2. **Go to Settings → Notifications**
3. **Disable repository notifications**

### Email Client
1. **Create filter for GitHub emails**
2. **Move to spam or delete automatically**
3. **Set up rules for specific notification types**

## 🚨 Emergency: Stop All GitHub Emails

### Nuclear Option
1. **Go to**: https://github.com/settings/emails
2. **Uncheck everything** in email preferences
3. **Or change email to a spam folder address**

### Temporary Solution
1. **Create email filter**: `from:noreply@github.com`
2. **Action**: Delete or move to spam
3. **Apply to all existing emails**

## ✅ Verification

### Test Your Settings
1. **Make a small change** to repository
2. **Check if you receive email**
3. **Adjust settings if needed**

### Check Notification Status
1. **Go to repository**
2. **Look at "Watch" button**
3. **Should show "Ignore" or custom settings**

## 📞 Support

If you're still getting spam after these changes:

1. **Check GitHub status**: https://www.githubstatus.com/
2. **Contact GitHub support**: https://support.github.com/
3. **Review account settings**: https://github.com/settings/

---

**Quick Summary**: Click "Watch" → "Ignore" on your repository to stop all email notifications.
