# 🗑️ Personal File Cleanup Guide

This guide will help you delete personal files that are still showing in your chat even after removing them from Google Cloud Storage.

## 🚨 The Problem

When you upload files to the chat, they are stored in **two places**:
1. **Google Cloud Storage** - The actual file content
2. **Google Cloud Firestore** - File metadata and chat messages

Even if you delete files from Cloud Storage, the chat messages in Firestore still contain references to these files, so they continue to show up in the chat interface.

## 🛠️ Solutions

### Option 1: Use the Cleanup Script (Recommended)

I've created a comprehensive cleanup script that can help you delete personal files from Firestore.

#### Prerequisites
Make sure you have the required environment variables set up:
```bash
# In your backend/.env file or environment
GOOGLE_SERVICE_ACCOUNT_KEY='{"type": "service_account", ...}'
GCS_BUCKET_NAME='labs-realtime-app-files'
```

#### Running the Script

1. **Interactive Mode** (Easiest):
```bash
cd /Users/michael.gabriel/monorepo
python cleanup_personal_files.py --interactive
```

2. **List All Files** (See what's there):
```bash
python cleanup_personal_files.py --list-files
python cleanup_personal_files.py --list-messages
```

3. **Delete by Filename**:
```bash
python cleanup_personal_files.py --delete-by-filename "personal_document.pdf"
```

4. **Delete by Sender Name**:
```bash
python cleanup_personal_files.py --delete-by-sender "Your Name"
```

5. **Delete by Date Range**:
```bash
python cleanup_personal_files.py --delete-by-date "2024-01-01" "2024-12-31"
```

6. **Delete ALL Files** (⚠️ DANGEROUS):
```bash
python cleanup_personal_files.py --delete-all-files
```

### Option 2: Use the Web Interface

I've added delete functionality to the chat interface:

1. **Hover over your messages** - You'll see a delete button (trash icon) appear
2. **Click the delete button** - Confirm the deletion
3. **Files will be deleted** from both Cloud Storage and Firestore

### Option 3: Use the API Endpoints

#### Delete Individual File
```bash
curl -X DELETE "https://backend-987275518911.us-central1.run.app/files/{file_id}"
```

#### Delete Individual Message
```bash
curl -X DELETE "https://backend-987275518911.us-central1.run.app/messages/{message_id}"
```

#### Bulk Delete Files
```bash
curl -X POST "https://backend-987275518911.us-central1.run.app/files/bulk-delete" \
  -H "Content-Type: application/json" \
  -d '{
    "sender_name": "Your Name",
    "filename_pattern": "personal",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }'
```

## 🔍 What Gets Deleted

When you delete a file, the system will:

1. ✅ **Delete from Google Cloud Storage** - Remove the actual file
2. ✅ **Delete from Firestore uploaded_files collection** - Remove file metadata
3. ✅ **Delete from Firestore messages collection** - Remove chat messages containing the file
4. ✅ **Update the chat interface** - Remove the file from the UI

## 🛡️ Safety Features

- **Confirmation dialogs** - You'll be asked to confirm before deletion
- **Selective deletion** - You can delete by filename, sender, date range, or file type
- **Error handling** - The system continues even if some deletions fail
- **Logging** - All operations are logged for transparency

## 🚀 Quick Start

1. **First, see what files you have**:
   ```bash
   python cleanup_personal_files.py --list-files
   ```

2. **Delete specific personal files**:
   ```bash
   python cleanup_personal_files.py --delete-by-filename "personal_file.pdf"
   ```

3. **Or use the interactive mode**:
   ```bash
   python cleanup_personal_files.py --interactive
   ```

## 📝 Notes

- **Backup**: Consider backing up important files before bulk deletion
- **Permissions**: Make sure you have the necessary Google Cloud permissions
- **Testing**: Test with a single file first before bulk operations
- **Recovery**: Deleted files cannot be recovered easily

## 🆘 Need Help?

If you encounter any issues:

1. Check the console output for error messages
2. Verify your Google Cloud credentials are set up correctly
3. Make sure you have the necessary permissions for Firestore and Cloud Storage
4. Try the interactive mode for a guided experience

---

**Remember**: Once files are deleted, they're gone from both storage systems. Make sure you really want to delete them before proceeding!
