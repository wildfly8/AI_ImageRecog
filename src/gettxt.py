import requests
from requests_ntlm import HttpNtlmAuth
import re

from tika import parser

def getText(url, ext, user, pswd):
    filename = "document"
    if ext in ["docx", "doc", "pdf", "pptx"]:
        try:
            r = requests.get(url, auth=HttpNtlmAuth(user, pswd), allow_redirects=True)
            with open(filename + "." + ext, 'wb') as f:
                f.write(r.content)
            text = parser.from_file(filename + "." + ext)["content"]
            if text is None:
                text = "NULL"
            else:
                text = text.replace('"', "'").replace('%', '%%').strip()
            return text
        except:
            return "NULL"
    elif ext == "msg":
        try:
            r = requests.get(url, auth=HttpNtlmAuth(user, pswd), allow_redirects=True)
            with open(filename + ".msg", 'wb') as f:
                f.write(r.content)
            text = parser.from_file(filename + ".msg")["content"]
            if text is None:

                text = "NULL"
            else:
                text = re.sub(r'image([\d]{3})\.([\w]{3})', '', text).replace('"',"'").replace('%', '%%').strip()
            return text
        except:
            return "NULL"
    else:
        try:
            r = requests.get(url, auth=HttpNtlmAuth(user, pswd), allow_redirects=True)
            with open(filename + "." + ext, "wb") as f:
                f.write(r.content)
            text = parser.from_file(filename + '.' + ext)["content"]
            if text is None:
                text = "NULL"
            else:
                text = text.replace('"', "'").replace('%', '%%').strip()
            return text
        except:
            return "NULL"
