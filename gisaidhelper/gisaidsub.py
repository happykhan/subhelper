"""
gisaidsub prepares files for gisaid sub using the interactive batch submission.

gisaidsub prepares files for gisaid sub using the interactive batch submission.

### CHANGE LOG ### 
2021-08-23 Nabil-Fareed Alikhan <nabil@happykhan.com>
    * Initial build
"""
from os import path, listdir, mkdir
import meta
import logging
import time
import sys
import argparse
from gishelper import merge_fasta_dir, load_yaml, format_table, write_table
import csv

epi = "Licence: " + meta.__licence__ +  " by " +meta.__author__ + " <" +meta.__author_email__ + ">"
logging.basicConfig()
log = logging.getLogger()


def main(args):
    logging.info(args)

    if not path.exists(args.outputdir):
        mkdir(args.outputdir)
    
    fasta_dict = {k: path.join(args.fasta_dir, k) for k in listdir(args.fasta_dir) if k.endswith('.fa')}
    sample_names = [x.split('.')[0] for x in fasta_dict.keys()] 

    custom_fields = load_yaml(args.field_mappings)
    global_values = load_yaml(args.global_values)
    metadata, sample_map = format_table(sample_names, args.meta_sheet, args.fasta_output, custom_fields, global_values)
    write_table(metadata, args.outputdir)



    # Create the merged fasta file.        
    merge_fasta_dir(fasta_dict, sample_map, path.join(args.outputdir, args.fasta_output))


if __name__ == '__main__':
    start_time = time.time()
    log.setLevel(logging.INFO)
    desc = __doc__.split('\n\n')[0].strip()
    parser = argparse.ArgumentParser(description=desc,epilog=epi)
    # Main parameters 
    parser.add_argument ('-v', '--verbose', action='store_true', default=False, help='verbose output')
    parser.add_argument('--version', action='version', version='%(prog)s ' + meta.__version__)
    parser.add_argument('--template', action='store', default='ori/20210222_EpiCoV_BulkUpload_Template.xls', help='Path to GISAID template')
    parser.add_argument('meta_sheet', action='store', help='path to metadata sheet')
    parser.add_argument('fasta_dir', action='store', help='directory of fasta files')     
    parser.add_argument('--outputdir', action='store', default='gisaidsubout', help='output directory')     
    parser.add_argument('--fasta_output', action='store', default='gisaidsub.fa', help='fasta output filename')     
    parser.add_argument('--field_mappings', action='store', default='scripts/pak-field-mapping.yaml', help='field mappings YAML')     
    parser.add_argument('--global_values', action='store', default='scripts/pak-globals.yaml', help='global values YAML')     
    
    parser.set_defaults(func=main)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else: 
        parser.print_help()    
    if args.verbose: 
        log.setLevel(logging.DEBUG)
        log.debug( "Executing @ %s\n"  %time.asctime())    
    if args.verbose: 
        log.debug("Ended @ %s\n"  %time.asctime())
        log.debug('total time in minutes: %d\n' %((time.time() - start_time) / 60.0))


