import imaplib
import os,glob
import email
import datetime
import pandas as pd
from dotenv import load_dotenv
from bs4 import BeautifulSoup as bs

load_dotenv('./.env')
class EmailExtractor():    
    cwd = os.getcwd()
    def set_search_rules(self,subject_header,start_date=None,end_date=None):
        search_criteria = "Subject '{}'".format(subject_header)
        if start_date and end_date:
            search_criteria += ' (Since {} Before {})'.format(start_date, end_date)
        return search_criteria
    
    def search_by_sender(self,sender):
        search_criteria = "From '{}'".format(sender)
        return search_criteria
    
    def attachment_download(self,search_criteria,download_dir):
        username = os.environ.get('email')
        password = os.environ.get('password')
        url = 'imap.gmail.com'
        detach_dir = download_dir#where to save attachments (default:current directory)
        #connecting to server
        mail = imaplib.IMAP4_SSL(url,993,timeout=60)
        mail.login(username,password)
        print("login successful")
        mail.select()
        response,items = mail.search(None,search_criteria)
        if response == 'OK':
            items = items[0].split() #getting the mails id
            for emailId in items:
                response,data = mail.fetch(emailId,"(RFC822)")# fetching the mail, "`(RFC822)`" means "get the whole stuff", but you can ask for headers only, etc
                email_body = data[0][1] #getting the mail content
                content = email.message_from_bytes(email_body)# parsing the mail content to get a mail object

                #get other info
                subject = content['Subject']
                sender = content['From']
                date = content['Date']
                body = ''

                #check if there is any attachments
                if content.get_content_maintype() != 'multipart':
                    continue

                for part in content.walk():
                    # multipart are just containers, so we skip them
                    if part.get_content_maintype() == 'multipart':
                        continue
                    # is this part an attachment:
                    if part.get('Content-Disposition') is None:
                        # Decode the payload
                        payload = part.get_payload(decode=True)
                        if payload:
                            soup = bs(payload,'html.parser')
                            # body += payload.decode('utf-8', 'ignore')
                            body += soup.get_text()
                    filename = part.get_filename()
                    counter = 1
                    if filename:
                        attachments_ext = os.path.splitext(filename)[1]
                        # Create folder according to attachment ext if it doesn't exist
                        ext_folder = os.path.join(detach_dir, attachments_ext[1:])
                        if not os.path.exists(ext_folder):
                            os.makedirs(ext_folder)

                        # Create filename if it doesn't exist
                        if not filename:
                            filename = 'part-%03d%s' % (counter, 'bin')
                            counter += 1

                        # Save the attachment in the extension folder
                        att_path = os.path.join(ext_folder, filename)

                        # Check if it's already there
                        if not os.path.isfile(att_path):
                            with open(att_path, 'wb') as fp:
                                fp.write(part.get_payload(decode=True))
                            print(f'{filename} downloaded')
                print(f'''
                    From : {sender}
                    Subject : {subject}
                    Date : {date}
                    Email Body: {body}
                    ''', )  
        
email_extractor = EmailExtractor()