#!/usr/bin/python3
import re

# Functions ###################################################################
def clean_pid(pid):
    clean_pid = str(pid)
    
    # Replace colons with hypen for hyperlinks
    clean_pid = pid.replace(':', '-')
    
    return clean_pid

def clean_title(dc_title):
    clean_title = str(dc_title)
    
    clean_title = clean_title.replace('[', '')
    clean_title = clean_title.replace(']', '')
    clean_title = clean_title.replace('"', '')
    clean_title = clean_title.replace("'", "")
    clean_title = clean_title.replace("\\n", "")
    clean_title = clean_title.replace("\\", "'")
    
    # Multiple spaces
    clean_title = re.sub(' +',' ', clean_title)
    
    return clean_title

def clean_date(dc_date):
    clean_date = str(dc_date)
    
    # Return if blank
    if clean_date == "":
        return ""
    
    # Clean string
    clean_date = clean_date.replace('[', '')
    clean_date = clean_date.replace(']', '')
    clean_date = clean_date.replace('"', '')
    clean_date = clean_date.replace("'", "")
    
    # Pull out 4 digit year only
    if "circa" not in clean_date:
        m = re.findall('(\d{4})', clean_date)
        try:
            clean_date = m[0]
        except IndexError:
            clean_date = None

        if clean_date == None:
            clean_date = ""
            
    # Clean up "circa"
    if "circa" in clean_date:
        clean_date = clean_date.replace("circa", "c.")
        
    # Add brackets to final string
    clean_date = f"({clean_date})"
    
    return clean_date
    
def clean_type_of_resource(type_of_resource):
    clean_type_of_resource = str(type_of_resource)
    
    # Clean string
    clean_type_of_resource = clean_type_of_resource.replace('[', '')
    clean_type_of_resource = clean_type_of_resource.replace(']', '')
    clean_type_of_resource = clean_type_of_resource.replace('"', '')
    clean_type_of_resource = clean_type_of_resource.replace("'", "")
        
    return clean_type_of_resource
    
def clean_collection_name(collection_name):
    clean_collection_name = str(collection_name)
    
    # Clean string
    clean_collection_name = clean_collection_name.replace('[', '')
    clean_collection_name = clean_collection_name.replace(']', '')
    clean_collection_name = clean_collection_name.replace('"', '')
    clean_collection_name = clean_collection_name.replace("'", "")
    clean_collection_name = clean_collection_name.replace(";", "")
    
    return clean_collection_name
    
def clean_mp4_size(mp4_size):
    clean_mp4_size = str(mp4_size)
    
    # Clean string
    clean_mp4_size = clean_mp4_size.replace('[', '')
    clean_mp4_size = clean_mp4_size.replace(']', '')
    clean_mp4_size = clean_mp4_size.replace('"', '')
    clean_mp4_size = clean_mp4_size.replace("'", "")
    clean_mp4_size = clean_mp4_size.replace(";", "")
    
    if clean_mp4_size == "":
        clean_mp4_size = "0"
    
    clean_mp4_size = int(clean_mp4_size)
    
    
    return clean_mp4_size