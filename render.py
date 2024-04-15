import csv
import pdf_converter
import datetime
import constants 
import utility
import constants
import ebooklib
import os

from ebooklib import epub

today = datetime.date.today()
# Set the locale to Croatian
# locale.setlocale(locale.LC_TIME, 'hr_HR.UTF-8')
# # Format today's date as '10 April 2024'
# formatted_date = today.strftime('%d. %B %Y')


def generate():

    csv_files = utility.list_csv_files(constants.data_folder_path)

    if not csv_files:
        print("Array is empty. exiting scritp")
        return

    ebooklib.DEFAULT_IGNORE_NCX = False

    # Process each CSV file
    for csv_file in csv_files:
        print("Processing CSV file:", csv_file)
        
        newspaper_title = ""
        newspaper_description = ""
        newspaper_content = ""

        # Read data from CSV file and populate articles array
        articles = []
        with open(csv_file, 'r', newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                article = {
                    'source': row['source'],
                    'description': row['description'],
                    'image_url': row['image'],
                    'title': row['title'],
                    'content': row['content']
                }
                articles.append(article)          

        for article in articles:

            newspaper_title = article['source']
            # newspaper_description = article['description']
       
            article_content = article['content']
            part1, part2, part3 = utility.split_article(article_content)
            
            newspaper_content += f"""
            <h1>{article['title']}</h1>
            <p>{part1}</p>
            <p>{part2}</p>
            <p>{part3}</p>            
            """

        # <img src="{article['image_url']}" alt="image" />
        # now we have newspaper content and we can create ebook
        book = epub.EpubBook()

        # add metadata
        book.set_identifier(newspaper_title + '-' + today.strftime("_%Y_%m_%d"))
        book.set_title(newspaper_title)
        book.set_language('hr')
        book.add_author('newspaper')

        # define style
        style_nav = '''
        @namespace epub "http://www.idpf.org/2007/ops";

        img{
            width:100%;
        }

        .date {
            font: 1em "Roboto Mono", monospace;
            text-align: center;
            width: 280px;
            margin: auto;
            margin-top: 10px;
            border-left: 1px solid black;
            border-right: 1px solid black;
        }

        header{
            font-size: 3em;
            color: #111;
            font-weight: bold;
            text-align: center;
            margin-top: 30px;
            padding-bottom: 15px;
            text-shadow: -1px 1px 0 white, -2px 2px 0 #111;
        }

        hr{
            margin-bottom: 50px;
            font: 1em "Roboto Mono", monospace;
            text-align: center;
            margin: auto;
            margin-top: 10px;
            border-left: 1px solid black;
            border-right: 1px solid black;
        }

        section{
            margin-top: 50px;
            -webkit-column-count: 3;
            -webkit-column-gap: 20px;
            -webkit-column-rule: 1px solid #A1A1A1;
            -moz-column-count: 3;
            -moz-column-gap: 20px;
            -moz-column-rule: 1px solid #A1A1A1;
            column-count: 3;
            column-gap: 20px;
            column-rule: 1px solid #A1A1A1;
            text-align: justify;
        }

        h1{
            margin-top:0;
            text-align: center;
        }
        '''

        # Add CSS file
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style_nav)
        book.add_item(nav_css)

        #header
        newspaper_header = f"""
            <header>{newspaper_title}</header>
            <hr />
            <div class="date">{today.strftime("%d/%m/%Y")}</div>
            <hr />
        """

        #content
        chapter = epub.EpubHtml(title = newspaper_title, file_name = newspaper_title + '.xhtml')

        chapter.content = newspaper_header + "<section>" + newspaper_content + "</section>"

        # add chapters to the book
        book.add_item(chapter)

        chapter.add_item(nav_css)

        # create spine
        book.spine = [newspaper_title, chapter]

        # add navigation files
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())


        # create epub file
        epub.write_epub(constants.build_folder_path + newspaper_title + '.epub', book, {})

        # create pdf file
        pdf_converter.epub_to_pdf(constants.build_folder_path + newspaper_title + '.epub', constants.build_folder_path + newspaper_title + '.pdf')