import imaplib
import os,glob
import email
import datetime
import pandas as pd

class EmailExtractor():    
    cwd = os.getcwd()

    def details(subject_header,date=(datetime.datetime.now()-datetime.timedelta(1)).strftime("%d-%b-%Y")):
        #email search criteria
        search_criteria = '(ON '+date+' Subject "'+subject_header+'")'
        return search_criteria
    
    def attachment_download(self,SUBJECT):
        username = ''
        password = ''
        url = 'imap.gmail.com'
        detach_dir = '.'#where to save attachments (default:current directory)
        #connecting to server
        mail = imaplib.IMAP4_SSL(url,993,timeout=60)
        mail.login(username,password)
        mail.select()
        response,items = mail.search(None,SUBJECT)
        items = items[0].split() #getting the mails id
        for emailId in items:
            response,data = mail.fetch(emailId,"(RFC822)")# fetching the mail, "`(RFC822)`" means "get the whole stuff", but you can ask for headers only, etc
            email_body = data[0][1] #getting the mail content
            content = email.message_from_string(str(email_body))# parsing the mail content to get a mail object

            #check if there is any attachments
            if content.get_content_maintype() != 'multipart':
                continue
            print(f"[{content["From"]}]:{content["Subject"]}")

            for part in content.walk():
                # multipart are just containers, so we skip them
                if part.get_content_maintype() == 'multipart':
                    continue
                # is this part an attachment:
                if part.get('Content-Disposition') is None:
                    continue
                filename = part.get_filename()
                counter = 1
                # if there is no filename, we create one with a counter to avoid duplicates
                if not filename:
                    filename = 'part-%03d%s' % (counter,'bin')
                    counter += 1
                att_path = os.path.join(detach_dir,filename)

                #check if it's already there
                if not os.path.isfile(att_path) :
                    fp = open(att_path,'wb')
                    fp.write(part.get_payload(decode=True))
                    fp.close()
            print(str(filename)+' downloaded')
            return filename
        
emailExtractor = EmailExtractor()
subject ="testing" 
emailExtractor.attachment_download(subject)