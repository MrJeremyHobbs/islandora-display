#!/usr/bin/python3
import os
import sys
import requests
import piexif
import re
import io
from PIL import Image, ImageFile
from helper_functions import *

# TODO ########################################################################
"""

-Add a list of bad pids to skip
-Further clean-up of metadata

"""

# Params ######################################################################
__version__ = 1.2

#ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = 1000000000

# Main ########################################################################
def main():
    # Generate SOLR request
    base_url = "https://digital.lib.calpoly.edu/islandora/rest/v1"

    query = f'mods_typeOfResource_ms:"still image"+OR+mods_typeOfResource_ms:"moving image"'
    limit_results = "PID,dc.title,dc.date,mods_typeOfResource_ms,mods_relatedItem_host_titleInfo_title_ms,fedora_datastream_latest_MP4_SIZE_ms"
    
    filter_query = '!RELS_EXT_hasModel_uri_ms:"info:fedora/islandora:compoundCModel"'\
                   'AND !mods_relatedItem_host_titleInfo_title_ms:"Sara Holmes Boutelle Papers"'\
                   'AND !mods_relatedItem_host_titleInfo_title_ms:"Gerber Oceano Collection"'\
                   'AND !mods_relatedItem_host_titleInfo_title_ms:"San Luis Obispo County Farmers\' Market Association Records"'\
                   'AND !mods_relatedItem_host_titleInfo_title_ms:"San Luis Obispo County Farmers\' Market Association Records;"'\
                   'AND !mods_relatedItem_host_titleInfo_title_ms:"With Our Own Eyes / Con Nuestros Propios Ojos Documentary Photography Project"'\
                   'AND !mods_relatedItem_host_titleInfo_title_ms:"Ezra Stoller Collection"'\
                   'AND !mods_relatedItem_host_titleInfo_title_ms:"Kathleen Goddard Jones Correspondence"'\
                   'AND !mods_relatedItem_host_titleInfo_title_ms:"Mark Mills Papers"'\
                   'AND !mods_relatedItem_host_titleInfo_title_ms:"William F. Cody Papers"'\
                   'AND !mods_relatedItem_host_titleInfo_title_ms:"William F. Cody Papers 2"'\
                   'AND !mods_relatedItem_host_titleInfo_title_ms:"Messinger Pacific Theater World War II Collection"'\
                   'AND !mods_relatedItem_host_titleInfo_title_ms:"Horner Architectural Photography Collection"'\
                   'AND !mods_relatedItem_host_titleInfo_title_ms:"Smith Family Papers on World War II"'\
                   'AND !mods_relatedItem_host_titleInfo_title_ms:"Edward G. Trinkkeller Papers"'
    
    rows = "10000000"

    # Make request
    solr_search_url = f'{base_url}/solr/{query}?fq={filter_query}&fl={limit_results}&rows={rows}'
    r = requests.get(solr_search_url)
    if r.status_code != 200:
        print(f"ERROR - {r.status_msg}")
        
    # Parse JSON dictionary and download each item via PID lookup
    json_dict = r.json()
    total_recs = json_dict["response"]["numFound"]
    print(f"{total_recs} found.")
    
    counter = 1
    for doc in json_dict["response"]["docs"]:    
        pid = doc.get("PID", "")
        pid_clean = clean_pid(doc.get("PID", ""))
        type_of_resource = clean_type_of_resource(doc.get("mods_typeOfResource_ms"))
        dc_title = clean_title(doc.get("dc.title", ""))
        dc_date = clean_date(doc.get("dc.date", ""))
        collection_name = clean_collection_name(doc.get("mods_relatedItem_host_titleInfo_title_ms", ""))
        mp4_size = clean_mp4_size(doc.get("fedora_datastream_latest_MP4_SIZE_ms", ""))
        
        # filter out large video files
        if type_of_resource == "moving image":
            if mp4_size > 400000000:
                print(f"[{counter} of {total_recs}] >>>>>>>> EXCEPTION - {pid} - {dc_title} - VIDEO FILE IS TOO LARGE/LONG")
                sys.stdout.flush()
                continue
            if mp4_size == 0:
                print(f"[{counter} of {total_recs}] >>>>>>>> EXCEPTION - {pid} - {dc_title} - VIDEO FILE IS NOT YET ON SERVER/TOO SMALL")
                sys.stdout.flush()
                continue
        
        # File formats
        if type_of_resource == 'still image':
            file_format = "JP2"
            file_extension = "jpg"
        if type_of_resource == 'moving image':
            file_format = "MP4"
            file_extension = "mp4"
            
        # Skip if already downloaded
        saved_file = f".\cache\{pid_clean}.{file_extension}"
        if os.path.exists(saved_file):
            print(f"[{counter} of {total_recs}] ALREADY DOWNLOADED - {pid} - {dc_title}")
            counter += 1
            sys.stdout.flush()
            continue

        # Get raw datastream
        datastream = requests.get(f"http://digital.lib.calpoly.edu/islandora/rest/v1/object/{pid}/datastream/{file_format}?[content, true]", stream=True)
        
        # Videos
        if type_of_resource == "moving image":
            with open(f".\\cache\\{pid_clean}.{file_extension}", "wb") as f:
                for chunk in datastream.iter_content(chunk_size=1024): 
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
            print(f"[{counter} of {total_recs}] DOWNLOADED - {pid} - {dc_title}")
            counter += 1
            sys.stdout.flush()
            
        # Pictures
        if type_of_resource == "still image":
            try:
                im = Image.open(io.BytesIO(datastream.content))
                sys.stdout.flush()
            except Exception as e:
                print(f"[{counter} of {total_recs}] >>>>>>>> EXCEPTION - {pid} - {dc_title} - {e}")
                counter += 1
                sys.stdout.flush()
                continue
        
            # Generate EXIF data and include caption information, encoded as UTF-8
            zeroth_ifd = {piexif.ImageIFD.Make: dc_title,
                          piexif.ImageIFD.Model: dc_date,
                          piexif.ImageIFD.Software: collection_name}
            exif_dict = {"0th":zeroth_ifd}
            
            try:
                exif_bytes = piexif.dump(exif_dict)
            except Exception as e:
                print(f"[{counter} of {total_recs}] >>>>>>>> EXCEPTION - {pid} - {dc_title} - {e}")
                counter += 1
                sys.stdout.flush()
                continue
                
            # Save as JPEG with EXIF information
            try:
                im.save(f".\\cache\\{pid_clean}.{file_extension}", 'JPEG', quality=95, exif=exif_bytes)
                print(f"[{counter} of {total_recs}] DOWNLOADED - {pid} - {dc_title}")
                counter += 1
                sys.stdout.flush()
            except Exception as e:
                print(f"[{counter} of {total_recs}] >>>>>>>> EXCEPTION - {pid} - {dc_title} - {e}")
                counter += 1
                sys.stdout.flush()
                continue
            
# Top-level ###################################################################        
if __name__ == "__main__":
    main()