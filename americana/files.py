import os
import hashlib
from urllib.request import urlopen
from os.path import basename
from django.core.files.storage import FileSystemStorage
import time
import requests
import re 
from decimal import *
import ssl

def is_downloadable(url):
    """
    Does the url contain a downloadable resource
    """
    h = requests.head(url, allow_redirects=True)
    header = h.headers
    content_type = header.get('content-type')
    if 'text' in content_type.lower():
        return False
    if 'html' in content_type.lower():
        return False
    return True

def download_file(url, fileName, FILE_LOCATION, UPLOAD_PATH):
    if is_downloadable(url):
        r = requests.get(url, allow_redirects=True)
        open(fileName, 'wb').write(r.content)
    else:
        return False
        
def get_file_hash(filename):
    BLOCKSIZE = 65536
    hasher = hashlib.sha1()
    with open(filename, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()
   
def get_file_size(file_path, size_type = False ):
   """ Get file in size in given unit like KB, MB or GB"""
   file_stats = os.stat(file_path)
   size = file_stats.st_size
   return str(size)
             
   
def file_from_url(url, FILE_LOCATION, UPLOAD_PATH, file_name=''):
    # ~ try:
    fs = FileSystemStorage(location=FILE_LOCATION)
    context = ssl.SSLContext()

    apkfile   = urlopen(url, context=context)
    file_extn = ''
    if file_name:
        file_nm, file_extn = os.path.splitext(apkfile.url)
        base_name = file_name+file_extn
    else:
        file_nm, file_extn = os.path.splitext(apkfile.url)
        base_name = basename(apkfile.url)
    
    filename = fs.save(base_name.replace(" ", ""), apkfile)
    if not file_extn and filename:
        return False
    
    upload_file_url = UPLOAD_PATH+filename
    file_path       = fs.path(filename)
    file_hash       = get_file_hash(file_path)
    file_size       = get_file_size(file_path, 'MB')
    
    return {"upload_url" : upload_file_url, 'size' : file_size, 'hash' : file_hash, 'filename' : filename, 'ext' : file_extn}
    # ~ except:
        # ~ return False



def file_upload(files, FILE_LOCATION, UPLOAD_PATH, fileName=''):
    
    fs = FileSystemStorage(location=FILE_LOCATION)
    try:
        fileExt   = files.name.split('.')
        file_extn = fileExt[1]
    except:
        file_extn = ''
    
    if fileName:
        file_name = fileName+'.'+file_extn
    else:
       file_name = files.name
           
    filename  = fs.save(file_name.replace(" ", ""), files)
    # ~ upload_file_url = fs.url(filename)
    upload_file_url = UPLOAD_PATH+filename
    file_path       = fs.path(filename)
    file_hash       = get_file_hash(file_path)
    file_size       = get_file_size(file_path, 'MB')
    return {"upload_url" : upload_file_url, 'size' : file_size, 'hash' : file_hash, 'filename' : filename, 'ext' : '.'+file_extn}
    
def create_file_with_content(file_name, FILE_LOCATION, content):    
    file_name = "file-" + str(file_name) + ".jpg"
    path = FILE_LOCATION + file_name
    with open(path, "w+") as f:
        f.write(str(content))
        
def create_dir(FILE_PATH):
    import pathlib
    access_rights = 0o755
    save_path  = FILE_PATH+time.strftime("%d-%m-%Y")
    check_path = pathlib.Path(save_path)
    if check_path.exists():
        pass
    else:
        os.mkdir(save_path, access_rights)
    return save_path


def create_image_base64(file_name, FILE_LOCATION, content):
    try:
        file_extn = '.jpg'
        file_name = "emp-" + str(file_name) + file_extn
        path = FILE_LOCATION + file_name
        with open(path, "w+") as f:
            f.write(str(content))
        
        if not file_extn and file_name:
            return False
        
        
        upload_file_url = UPLOAD_PATH+file_name
        file_path       = path
        file_hash       = get_file_hash(file_path)
        file_size       = get_file_size(file_path, 'MB')
        
        return {"upload_url" : upload_file_url, 'size' : file_size, 'hash' : file_hash, 'filename' : filename, 'ext' : file_extn}
    except:
        return False

    
def api_file(file_name, FILE_PATH, content):
    import time
    FILE_LOCATION = '/var/www/html/api/'
    path = create_dir(FILE_LOCATION+FILE_PATH) + '/'+ time.strftime("%H-%M-%S") + str(file_name)
    with open(path, "a") as myfile:
        myfile.write(str(content)+" \n")
        
        
# compare app greater version
def compare_appv(current_app, new_app):
    if (re.search('[a-zA-Z]', current_app) == None) and (re.search('[a-zA-Z]', new_app) == None):
        compare_version = Decimal(new_app).compare(Decimal(current_app))
    else:
        compare_version = ''
    if compare_version: 
        if compare_version != 1:
            return False
        else:
            return True 
    else:
        return True


    
