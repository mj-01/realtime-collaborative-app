#!/usr/bin/env python3
"""
Script to delete personal files from Firestore collections.
This script will help you remove personal files that are still showing in chats
even after deleting them from Google Cloud Storage.

Usage:
    python cleanup_personal_files.py --help
    python cleanup_personal_files.py --list-files
    python cleanup_personal_files.py --delete-by-filename "personal_file.pdf"
    python cleanup_personal_files.py --delete-by-sender "Your Name"
    python cleanup_personal_files.py --delete-by-date "2024-01-01" "2024-12-31"
    python cleanup_personal_files.py --delete-all-files  # DANGEROUS - deletes ALL files
"""

import os
import sys
import argparse
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from google.cloud import firestore, storage
from google.cloud.exceptions import NotFound
from google.oauth2 import service_account
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PersonalFileCleaner:
    def __init__(self):
        """Initialize Firestore and Cloud Storage clients"""
        self.db = None
        self.storage_client = None
        self.bucket = None
        self._init_clients()
    
    def _init_clients(self):
        """Initialize Google Cloud clients"""
        try:
            # Try to use service account key from environment variable
            service_account_key = os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY')
            if service_account_key:
                credentials_info = json.loads(service_account_key)
                credentials = service_account.Credentials.from_service_account_info(credentials_info)
                self.db = firestore.Client(credentials=credentials)
                self.storage_client = storage.Client(credentials=credentials)
                print("✅ Using service account credentials from environment variable")
            else:
                # Use default credentials
                self.db = firestore.Client()
                self.storage_client = storage.Client()
                print("✅ Using default credentials")
            
            # Initialize Cloud Storage bucket
            bucket_name = os.getenv('GCS_BUCKET_NAME', 'labs-realtime-app-files')
            self.bucket = self.storage_client.bucket(bucket_name)
            print(f"✅ Connected to Firestore and Cloud Storage bucket: {bucket_name}")
            
        except Exception as e:
            print(f"❌ Error initializing clients: {e}")
            sys.exit(1)
    
    def list_all_files(self) -> List[Dict[str, Any]]:
        """List all files in the uploaded_files collection"""
        print("📋 Listing all files in Firestore...")
        files = []
        
        try:
            docs = self.db.collection('uploaded_files').stream()
            for doc in docs:
                file_data = doc.to_dict()
                file_data['doc_id'] = doc.id
                files.append(file_data)
            
            print(f"Found {len(files)} files in uploaded_files collection")
            return files
            
        except Exception as e:
            print(f"❌ Error listing files: {e}")
            return []
    
    def list_file_messages(self) -> List[Dict[str, Any]]:
        """List all file messages in the messages collection"""
        print("📋 Listing all file messages in Firestore...")
        file_messages = []
        
        try:
            docs = self.db.collection('messages').where('type', '==', 'file').stream()
            for doc in docs:
                message_data = doc.to_dict()
                message_data['doc_id'] = doc.id
                file_messages.append(message_data)
            
            print(f"Found {len(file_messages)} file messages in messages collection")
            return file_messages
            
        except Exception as e:
            print(f"❌ Error listing file messages: {e}")
            return []
    
    def delete_file_by_filename(self, filename: str) -> bool:
        """Delete files by original filename"""
        print(f"🔍 Searching for files with filename: {filename}")
        
        deleted_count = 0
        
        # Delete from uploaded_files collection
        try:
            docs = self.db.collection('uploaded_files').where('original_name', '==', filename).stream()
            for doc in docs:
                file_data = doc.to_dict()
                print(f"🗑️  Deleting file: {file_data['original_name']} (ID: {doc.id})")
                
                # Delete from Cloud Storage if it still exists
                try:
                    blob = self.bucket.blob(file_data['unique_name'])
                    if blob.exists():
                        blob.delete()
                        print(f"   ✅ Deleted from Cloud Storage: {file_data['unique_name']}")
                    else:
                        print(f"   ⚠️  File not found in Cloud Storage: {file_data['unique_name']}")
                except Exception as e:
                    print(f"   ⚠️  Error deleting from Cloud Storage: {e}")
                
                # Delete from Firestore
                doc.reference.delete()
                deleted_count += 1
                print(f"   ✅ Deleted from Firestore: {doc.id}")
                
        except Exception as e:
            print(f"❌ Error deleting from uploaded_files: {e}")
            return False
        
        # Delete from messages collection
        try:
            docs = self.db.collection('messages').where('type', '==', 'file').where('fileName', '==', filename).stream()
            for doc in docs:
                print(f"🗑️  Deleting file message: {doc.id}")
                doc.reference.delete()
                deleted_count += 1
                print(f"   ✅ Deleted file message from Firestore: {doc.id}")
                
        except Exception as e:
            print(f"❌ Error deleting from messages: {e}")
            return False
        
        print(f"✅ Successfully deleted {deleted_count} records for filename: {filename}")
        return True
    
    def delete_files_by_sender(self, sender_name: str) -> bool:
        """Delete files by sender name"""
        print(f"🔍 Searching for files uploaded by: {sender_name}")
        
        deleted_count = 0
        
        # Delete from messages collection
        try:
            docs = self.db.collection('messages').where('type', '==', 'file').where('sender', '==', sender_name).stream()
            for doc in docs:
                message_data = doc.to_dict()
                print(f"🗑️  Deleting file message: {message_data.get('fileName', 'Unknown')} from {sender_name}")
                
                # Also delete from uploaded_files if we have the fileId
                if 'fileId' in message_data:
                    try:
                        file_doc = self.db.collection('uploaded_files').document(message_data['fileId'])
                        if file_doc.get().exists:
                            file_data = file_doc.get().to_dict()
                            
                            # Delete from Cloud Storage
                            try:
                                blob = self.bucket.blob(file_data['unique_name'])
                                if blob.exists():
                                    blob.delete()
                                    print(f"   ✅ Deleted from Cloud Storage: {file_data['unique_name']}")
                            except Exception as e:
                                print(f"   ⚠️  Error deleting from Cloud Storage: {e}")
                            
                            # Delete from uploaded_files
                            file_doc.delete()
                            print(f"   ✅ Deleted from uploaded_files: {message_data['fileId']}")
                    except Exception as e:
                        print(f"   ⚠️  Error deleting from uploaded_files: {e}")
                
                # Delete the message
                doc.reference.delete()
                deleted_count += 1
                print(f"   ✅ Deleted file message: {doc.id}")
                
        except Exception as e:
            print(f"❌ Error deleting by sender: {e}")
            return False
        
        print(f"✅ Successfully deleted {deleted_count} file messages from sender: {sender_name}")
        return True
    
    def delete_files_by_date_range(self, start_date: str, end_date: str) -> bool:
        """Delete files uploaded within a date range"""
        print(f"🔍 Searching for files uploaded between {start_date} and {end_date}")
        
        try:
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
        except ValueError as e:
            print(f"❌ Invalid date format. Use YYYY-MM-DD: {e}")
            return False
        
        deleted_count = 0
        
        # Delete from uploaded_files collection
        try:
            docs = self.db.collection('uploaded_files').where('upload_time', '>=', start_dt).where('upload_time', '<=', end_dt).stream()
            for doc in docs:
                file_data = doc.to_dict()
                print(f"🗑️  Deleting file: {file_data['original_name']} (uploaded: {file_data['upload_time']})")
                
                # Delete from Cloud Storage
                try:
                    blob = self.bucket.blob(file_data['unique_name'])
                    if blob.exists():
                        blob.delete()
                        print(f"   ✅ Deleted from Cloud Storage: {file_data['unique_name']}")
                except Exception as e:
                    print(f"   ⚠️  Error deleting from Cloud Storage: {e}")
                
                # Delete from Firestore
                doc.reference.delete()
                deleted_count += 1
                print(f"   ✅ Deleted from Firestore: {doc.id}")
                
        except Exception as e:
            print(f"❌ Error deleting from uploaded_files: {e}")
            return False
        
        # Delete from messages collection
        try:
            docs = self.db.collection('messages').where('type', '==', 'file').where('timestamp', '>=', start_dt).where('timestamp', '<=', end_dt).stream()
            for doc in docs:
                print(f"🗑️  Deleting file message: {doc.id}")
                doc.reference.delete()
                deleted_count += 1
                print(f"   ✅ Deleted file message: {doc.id}")
                
        except Exception as e:
            print(f"❌ Error deleting from messages: {e}")
            return False
        
        print(f"✅ Successfully deleted {deleted_count} records between {start_date} and {end_date}")
        return True
    
    def delete_all_files(self) -> bool:
        """Delete ALL files (DANGEROUS - use with caution)"""
        print("⚠️  WARNING: This will delete ALL files and file messages!")
        confirmation = input("Type 'DELETE ALL FILES' to confirm: ")
        
        if confirmation != "DELETE ALL FILES":
            print("❌ Operation cancelled")
            return False
        
        deleted_count = 0
        
        # Delete all from uploaded_files collection
        try:
            docs = self.db.collection('uploaded_files').stream()
            for doc in docs:
                file_data = doc.to_dict()
                print(f"🗑️  Deleting file: {file_data['original_name']}")
                
                # Delete from Cloud Storage
                try:
                    blob = self.bucket.blob(file_data['unique_name'])
                    if blob.exists():
                        blob.delete()
                        print(f"   ✅ Deleted from Cloud Storage: {file_data['unique_name']}")
                except Exception as e:
                    print(f"   ⚠️  Error deleting from Cloud Storage: {e}")
                
                # Delete from Firestore
                doc.reference.delete()
                deleted_count += 1
                print(f"   ✅ Deleted from Firestore: {doc.id}")
                
        except Exception as e:
            print(f"❌ Error deleting from uploaded_files: {e}")
            return False
        
        # Delete all file messages
        try:
            docs = self.db.collection('messages').where('type', '==', 'file').stream()
            for doc in docs:
                print(f"🗑️  Deleting file message: {doc.id}")
                doc.reference.delete()
                deleted_count += 1
                print(f"   ✅ Deleted file message: {doc.id}")
                
        except Exception as e:
            print(f"❌ Error deleting from messages: {e}")
            return False
        
        print(f"✅ Successfully deleted {deleted_count} records")
        return True
    
    def interactive_cleanup(self):
        """Interactive cleanup mode"""
        print("\n🔧 Interactive Personal File Cleanup")
        print("=" * 50)
        
        while True:
            print("\nOptions:")
            print("1. List all files")
            print("2. List file messages")
            print("3. Delete by filename")
            print("4. Delete by sender name")
            print("5. Delete by date range")
            print("6. Delete all files (DANGEROUS)")
            print("0. Exit")
            
            choice = input("\nEnter your choice (0-6): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                files = self.list_all_files()
                for i, file_data in enumerate(files, 1):
                    print(f"{i}. {file_data['original_name']} (ID: {file_data['doc_id']}) - {file_data['upload_time']}")
            elif choice == "2":
                messages = self.list_file_messages()
                for i, msg in enumerate(messages, 1):
                    print(f"{i}. {msg.get('fileName', 'Unknown')} from {msg.get('sender', 'Unknown')} - {msg.get('timestamp', 'Unknown')}")
            elif choice == "3":
                filename = input("Enter filename to delete: ").strip()
                if filename:
                    self.delete_file_by_filename(filename)
            elif choice == "4":
                sender = input("Enter sender name to delete: ").strip()
                if sender:
                    self.delete_files_by_sender(sender)
            elif choice == "5":
                start_date = input("Enter start date (YYYY-MM-DD): ").strip()
                end_date = input("Enter end date (YYYY-MM-DD): ").strip()
                if start_date and end_date:
                    self.delete_files_by_date_range(start_date, end_date)
            elif choice == "6":
                self.delete_all_files()
            else:
                print("❌ Invalid choice. Please try again.")

def main():
    parser = argparse.ArgumentParser(description="Clean up personal files from Firestore")
    parser.add_argument("--list-files", action="store_true", help="List all files")
    parser.add_argument("--list-messages", action="store_true", help="List all file messages")
    parser.add_argument("--delete-by-filename", type=str, help="Delete files by filename")
    parser.add_argument("--delete-by-sender", type=str, help="Delete files by sender name")
    parser.add_argument("--delete-by-date", nargs=2, metavar=("START_DATE", "END_DATE"), help="Delete files by date range (YYYY-MM-DD)")
    parser.add_argument("--delete-all-files", action="store_true", help="Delete ALL files (DANGEROUS)")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    cleaner = PersonalFileCleaner()
    
    if args.interactive:
        cleaner.interactive_cleanup()
    elif args.list_files:
        cleaner.list_all_files()
    elif args.list_messages:
        cleaner.list_file_messages()
    elif args.delete_by_filename:
        cleaner.delete_file_by_filename(args.delete_by_filename)
    elif args.delete_by_sender:
        cleaner.delete_files_by_sender(args.delete_by_sender)
    elif args.delete_by_date:
        cleaner.delete_files_by_date_range(args.delete_by_date[0], args.delete_by_date[1])
    elif args.delete_all_files:
        cleaner.delete_all_files()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
