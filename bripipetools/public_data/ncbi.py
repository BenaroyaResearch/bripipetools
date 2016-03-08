import _mypath
from bripipetools.util import string_ops as strings
import os, sys, re
import GEOparse
import shutil
import urllib2
from contextlib import closing

# list supplementary files for a GEO GSE accession
def get_supplementary_files(gse):
    supp_file_dict = {}

    # loop through all GSM samples
    for gsm_name, gsm in gse.gsms.iteritems():

        # parse metadata items to find supplementary files
        for key, value in gsm.metadata.iteritems():
            if re.search('supplementary_file', key):
                # if the supplementary file has a file extension, add to dictionary;
                # otherwise, ignore (requires alternative collection)
                supp_type = strings.matchdefault('\..*', os.path.basename(value[0]))
                if len(supp_type):
                    supp_file_dict.setdefault(supp_type, []).append(value[0])

    return supp_file_dict

def select_supplementary_filetype(keys):
    print "\nFound the following supplemenmtary filetypes:"
    for i, k in enumerate(keys):
        print("%3d : %s" % (i, k))

    k_i = raw_input("\nType the number of the filetype you wish to collect or hit enter to finish: ")
    # TODO: add the option (while loop) to add additional filetypes
    if len(k_i):
        selected_key = keys[int(k_i)]

    return selected_key

def collect_supplementary_files(gse, target_dir='./'):
    supp_file_dict = get_supplementary_files(gse)
    selected_type = select_supplementary_filetype(supp_file_dict.keys())

    supplementary_files = supp_file_dict[selected_type]
    print("\nCollecting %d supplementary files with extension '%s'..."
          % (len(supplementary_files), selected_type))

    for supp_f in supplementary_files:
        gsm_name = strings.matchdefault('GSM[0-9]+', supp_f)
        print('- Downloading file for %s...' % gsm_name),
        sys.stdout.flush()

        target_f = os.path.join(target_dir, os.path.basename(supp_f))
        with closing(urllib2.urlopen(supp_f)) as r:
            with open(target_f, 'wb') as f:
                shutil.copyfileobj(r, f)
        print('done.')
        break

def download_gse_data(acc, target_dir='./'):
    if not os.path.isdir(target_dir):
        os.makedirs(target_dir)
    gse = gse = GEOparse.get_GEO(geo=acc, destdir=target_dir)
    collect_supplementary_files(gse, target_dir)
