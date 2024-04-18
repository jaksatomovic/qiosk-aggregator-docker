#!/usr/bin/env python3
import csv
import spider
import render
import utility
import os
import datetime
import constants
import notification
import logging
import sys

# Configure logging to write to STDOUT
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


from dotenv import load_dotenv
from database_manager import DatabaseManager

today = datetime.date.today()

# Configure logging to write to STDOUT
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class Main:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        self.db_manager = DatabaseManager.get_instance()

        # Setup project
        self.db_manager.connect()
        database_ok = self.db_manager.check_database()
        self.db_manager.disconnect()

        if not database_ok:
            print("Database is not set!")
            return

        utility.build_folder_structure()

    def run(self):
        # Perform operations here
        print("Main class is running")

        self.db_manager.connect()
        journals = self.db_manager.get_journals()
        self.db_manager.disconnect()
        
        for journal in journals:
            # Call spider.get_news with the fetched data  
            spider.get_news(journal, self.db_manager)          

        self.process_files()
         
        self.db_manager.connect()
        self.db_manager.execute_query(''' DROP TABLE temp_data ''')
        self.db_manager.disconnect()

        # self.store_files()
        utility.delete_all_files(constants.build_folder_path)
        # notification.send_alert("INK", "<h1>Scraping successful!</h1>")

    def process_files(self):
        render.generate(self.db_manager)

    def store_files(self):
        epub_files, pdf_files = utility.get_files_by_extension('build/')  
        # Merge epub_data and pdf_data into one list
        file_data = [(os.path.basename(file), open(file, 'rb').read()) for file in epub_files + pdf_files]

        # id	title	newspaper_date	file_name	file_data	file_data_content_type	epub_file	epub_file_content_type	journal_id	


        self.db_manager.connect()        
        for file_name, file_data in file_data:
            newspaper = {
                'title': file_name.split('.')[0],
                'newspaper_date': today.strftime("%d/%m/%Y"),
                'file_name': file_name,
                'file_data_content_type': file_data,
                'epub_file': file_name,
                'epub_file_content_type': file_data,
                'journal_id': 1
            }
            self.db_manager.create_newspaper(newspaper)

        self.db_manager.disconnect()

if __name__ == "__main__":
    # Instantiate and run the main class
    main = Main()
    main.run()


