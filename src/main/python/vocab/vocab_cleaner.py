# Copyright 2022 The Board of Trustees of The Leland Stanford Junior University.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import csv
import sys
import argparse

def pre_proccess_vocab (infile):
    print(infile)
    # Change source_vocabulary_id to be uppercase, source_concept_class_id values to be lowercase and source_domain_id values to capitalized
    with open(infile, 'rt') as f:
        reader = csv.reader(f, skipinitialspace=True, delimiter=',', quotechar='"')
        with open("outfile", "w") as fo:
            writer = csv.writer(fo)
            row_num = 0
            for rec in reader:
                new_rec = []
                col_num = 0
                for e in rec:
                    if (row_num >= 1):
                        if (col_num == 2):
                            e = e.upper()
                        if (col_num == 3):
                            e = e.capitalize()
                        if (col_num == 4):
                            e = e.lower()
                    col_num = col_num + 1
                    new_rec.append(e.strip().strip('\r'))
                row_num = row_num + 1
                writer.writerow(new_rec)
                
def main():
    parser = argparse.ArgumentParser(description="Utitlity for cleaning up the custom vocabulary mapping csv file")
    
    parser.add_argument("infile", help="Costum vocabulary csv file to be cleaned")
    # parser.add_argument("outfile", help="Costum vocabulary csv file after cleanup")
    
    args = parser.parse_args()
    pre_proccess_vocab(args.infile)
    
if __name__ == '__main__':
    sys.exit(main())