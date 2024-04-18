#!/usr/bin/env python3

import os
import shutil
import datetime
import argparse
import subprocess
import logging

# Set up logging
logging.basicConfig(filename='backup_log.txt', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Function to create a backup zip file
def create_backup(project_dir, backup_dir):
   try:
       backup_filename = f"{os.path.basename(project_dir)}_{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.zip"
       backup_path = os.path.join(backup_dir, backup_filename)
       shutil.make_archive(backup_path.replace('.zip', ''), 'zip', project_dir)
       logging.info(f"Backup created: {backup_path}")
       return backup_path
   except Exception as e:
       logging.error(f"Error creating backup: {e}")
       return None

# Function to upload backup to Google Drive
def upload_to_google_drive(backup_path, drive_folder):
   try:
       # Replace the following line with the appropriate CLI tool and command
       subprocess.run(['gdrive', 'upload', '--parent', drive_folder, backup_path], check=True)
       logging.info(f"Backup uploaded to Google Drive: {backup_path}")
   except subprocess.CalledProcessError as e:
       logging.error(f"Error uploading backup to Google Drive: {e}")

# Function to delete old backups
def delete_old_backups(backup_dir, keep_daily=7, keep_weekly=4, keep_monthly=3):
   try:
       # Get a list of all backup files
       backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.zip')]
       backup_files.sort(reverse=True)

       # Delete old daily backups
       daily_backups = [f for f in backup_files if f.startswith(os.path.basename(backup_dir))]
       for i, backup_file in enumerate(daily_backups[keep_daily:]):
           os.remove(os.path.join(backup_dir, backup_file))
           logging.info(f"Deleted old daily backup: {backup_file}")

       # Delete old weekly backups
       weekly_backups = [f for f in backup_files if f.startswith(f"{os.path.basename(backup_dir)}_") and f not in daily_backups[:keep_daily]]
       weekly_backups_to_delete = weekly_backups[keep_weekly:]
       for backup_file in weekly_backups_to_delete:
           os.remove(os.path.join(backup_dir, backup_file))
           logging.info(f"Deleted old weekly backup: {backup_file}")

       # Delete old monthly backups
       monthly_backups = [f for f in backup_files if f not in daily_backups[:keep_daily] and f not in weekly_backups[:keep_weekly]]
       monthly_backups_to_delete = monthly_backups[keep_monthly:]
       for backup_file in monthly_backups_to_delete:
           os.remove(os.path.join(backup_dir, backup_file))
           logging.info(f"Deleted old monthly backup: {backup_file}")

   except Exception as e:
       logging.error(f"Error deleting old backups: {e}")

# Function to send cURL request on successful backup
def send_curl_request(project_name, backup_date):
   try:
       subprocess.run(['curl', '-X', 'POST', '-H', 'Content-Type: application/json', '-d', f'{{"project": "{project_name}", "date": "{backup_date}", "test": "BackupSuccessful"}}', 'https://webhook.site/your-unique-url'], check=True)
       logging.info("cURL request sent successfully")
   except subprocess.CalledProcessError as e:
       logging.error(f"Error sending cURL request: {e}")

# Main function
def main():
   # Parse command-line arguments
   parser = argparse.ArgumentParser(description='Backup management script')
   parser.add_argument('--project-dir', required=True, help='Path to the project directory')
   parser.add_argument('--backup-dir', required=True, help='Path to the backup directory')
   parser.add_argument('--drive-folder', required=True, help='Google Drive folder ID to upload backups')
   parser.add_argument('--disable-curl', action='store_true', help='Disable sending cURL request')
   args = parser.parse_args()

   # Create backup
   backup_path = create_backup(args.project_dir, args.backup_dir)
   if backup_path:
       # Upload backup to Google Drive
       upload_to_google_drive(backup_path, args.drive_folder)

       # Delete old backups
       delete_old_backups(args.backup_dir)

       # Send cURL request on successful backup
       if not args.disable_curl:
           send_curl_request(os.path.basename(args.project_dir), backup_path.split('_')[1].split('-')[0])

if __name__ == '__main__':
   main()
