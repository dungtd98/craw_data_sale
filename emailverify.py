import os
import datetime, time
import pycurl
import tempfile
import requests

class EmailListVerifyBulk():

    def __init__(self, key, user_file):
        datenow = datetime.datetime.now()
        self.key = key
        self.name = 'File' + datenow.strftime("%Y-%m-%d_%H-%M-%S")
        self.user_file = user_file
        self.url = f'https://apps.emaillistverify.com/api/verifApiFile?secret={key}&filename={self.name}'

    def upload(self):
        with tempfile.NamedTemporaryFile(delete=False) as infile:
            c = pycurl.Curl()
            c.setopt(c.POST, 1)
            c.setopt(c.URL, self.url)
            c.setopt(c.HTTPPOST, [('file_contents', (
                        c.FORM_FILE, self.user_file,
                        c.FORM_CONTENTTYPE, 'text/plain',
                        c.FORM_FILENAME, self.name.replace(' ', '_'),)),])
            c.setopt(c.WRITEFUNCTION, infile.write)
            c.setopt(c.VERBOSE, 1)
            c.perform()
            c.close()
            self.tempfile_path = infile.name

    def get_info(self):
        while True:
            with open(self.tempfile_path, 'r') as f:
                ids = f.read().strip()
            url = f'https://apps.emaillistverify.com/api/getApiFileInfo?secret={self.key}&id={ids}'
            r = requests.get(url)
            response_text = r.text
            print(response_text)
            
            # Split the response text to check the status
            parts = response_text.split('|')
            print("PARTS>>>",parts)
            if len(parts) > 5:
                status = parts[5]
                if status == 'finished':
                    download_link = parts[-2]
                    return download_link
                else:
                    
                    time.sleep(3) 
            else:
                raise ValueError("Unexpected response format")
            