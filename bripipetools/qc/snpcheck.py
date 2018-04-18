"""
Class and methods to perform routine SNP check on all processed libraries.
"""

import logging
import os
import csv
import requests
import json

import pandas as pd

from .. import parsing
from .. import util

logger = logging.getLogger(__name__)


class SnpChecker(object):
    """
    Given workflow batch data, builds "families" of libraries from the same
    donor. SNPs called in these libraries are then analyzed to generate a 
    kinship score to help identify mislabeled libraries.
    """
    def __init__(self, workflowbatch_data, genomics_root, db):
        logger.debug("creating an instance of `SnpChecker` "
                     "with genomics root '{}'"
                     .format(genomics_root))
        self.workflowbatch_data = workflowbatch_data
        self.genomics_root = genomics_root
        self.db = db
        self.lib_list = dict()      # {lib: {libfamily:, write:, fname:}}
        self.family_list = dict()   # {libfamily: [libs]}
        
    def _manually_assign_family(self, libid):
        """
        Reads from stdin to allow user to manually assign a family ID to a lib
        """
        show_prompt = True
        while(show_prompt):
            for n,s in enumerate(sorted(self.lib_list.iterkeys())):
                print("{}:\t{}".format(n,s))
            
            famid = raw_input("Please enter an ID from the list to assign a \n"
                              "family ID for this library, or enter to skip:\n")
            
            if(not len(famid)):
                return
            
            if famid in self.lib_list:
                show_prompt = False
            else:
                print("{} was not found in the list.\n".format(famid))                
        
        self.lib_list[libid]['libfamily'] = famid
        self.lib_list[libid]['write'] = True
        # update the family list
        if (not famid in self.family_list):
            self.family_list[famid] = []
        self.family_list[famid].append(libid)
        
    def _build_lib_list(self):
        """
        Build a dictionary of libs. Each lib key will contain as a value a dict
        with 'fname' (the filename), 'write' (whether to perform snpcheck on
        this lib), and 'libfamily' (an identifier for libs in the same 'family')
        """
        # build the liblist without any family info
        for s in self.workflowbatch_data['samples']:
            for k in s:
                if (k['tag'] == 'bcftools_call_snps_vcf_out' and
                    k['name'] == 'to_path'):
                    currFname = os.path.normpath(k['value'])
                    currLib = parsing.get_library_id(currFname)
                    self.lib_list[currLib] = {'fname': currFname,
                                              'write': False}
        
        if (not len(self.lib_list)):
            return
        
        # fill in the family info                 
        for lib in sorted(self.lib_list.iterkeys()):
            # Check if lib already has a family assigned
            if ('libfamily' in self.lib_list[lib]):
                self.lib_list[lib]['write'] = True
                curr_fam = self.lib_list[lib]['libfamily']
                if (not curr_fam in self.family_list):
                    self.family_list[curr_fam] = []
                self.family_list[curr_fam].append(lib)
                continue
            
            # If lib not already assigned to a family, try to get that info
            api= "https://researchdb.benaroyaresearch.org/libId/associatedLibs/"
            api += lib
            logger.debug("requesting data for {} from API at {}"
                         .format(lib, api))
            lib_api_reponse = requests.get(api)
            logger.debug("API returned with status {}"
                         .format(lib_api_reponse.status_code))
                         
            # if API inaccessible...
            if (lib_api_reponse.status_code != 200):
                print("Requesting the API at {} returned a status code of {}. "
                      .format(api, lib_api_reponse.status_code))
                self._manually_assign_family(lib)
            
            else:
                api_data = json.loads(lib_api_reponse.content)
                # if API failed...
                if (api_data['retCode'] != 1):
                    print("The API at {} responded with a return code of {}. "
                          .format(api, api_data['retCode']))
                    self._manually_assign_family(lib)
                
                # if API returned no matches...
                elif (not len(api_data['libIds'])):
                    print("The API at {} could not find any libs related to {}. "
                          .format(api, lib))
                    self._manually_assign_family(lib)
                
                # API returned matches! Label all matches with the current lib
                # as the family ID. This will make looking up the donor easier.
                else:
                    related_libs = api_data['libIds']
                    for rel_l in related_libs:
                        if rel_l in self.lib_list:
                            self.lib_list[rel_l]['libfamily'] = lib
                            self.lib_list[rel_l]['write'] = True
                            if (not lib in self.family_list):
                                self.family_list[lib] = []
                            self.family_list[lib].append(rel_l)
                
                
    def _write_family_files(self):
        """
        Writes a <family>.lst file for all families in self.family_list
        """
        all_lib_refs = []
        for curr_fam in self.family_list:
            vcf_pathname = self.lib_list[curr_fam]['fname']
            snp_dir = os.path.dirname(vcf_pathname)
            snp_dir = util.swap_root(snp_dir, 'genomics', self.genomics_root)
            
            family_libs = self.family_list[curr_fam]
            f = open(os.path.join(snp_dir, curr_fam+"_family.lst"), 'w')
            for lib in family_libs:
                curr_fname = os.path.basename(self.lib_list[lib]['fname'])
                curr_libref = os.path.splitext(curr_fname)[0]
                all_lib_refs.append(curr_libref)
                f.write(curr_libref + "\n")
            f.close()
        # Write an all libs family
        if (len(all_lib_refs)):
            f = open(os.path.join(snp_dir, "all-libs_family.lst"), 'w')
            for curr_libref in all_lib_refs:
                f.write(curr_libref + "\n")
            f.close()
                
                          
    def check_snps(self):
        self._build_lib_list()
        self._write_family_files()
        
        quit()