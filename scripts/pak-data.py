from os import path, listdir, mkdir
import logging 
import csv 
from shutil import copy

logging.basicConfig(level=logging.DEBUG)

# Fetch valid sample names and paths 
def main(data_dirs, outputdir):
    if not path.exists(outputdir):
        mkdir(outputdir)    
    sample_dict = {}
    failed = []  
    for data_dir in data_dirs:
        qc_file = [path.join(data_dir, x) for x in listdir(data_dir) if x.endswith('.qc.csv')] 
        if len(qc_file) == 1:
            files = path.join(data_dir, 'qc_climb_upload')
            seq_dir = path.join(files, listdir(files)[0])

            sample_dict.update({x['sample_name'].split('_')[0] : x for x in csv.DictReader(open(qc_file[0]), dialect=csv.excel)  if x['qc_pass'] == 'TRUE'})
            for sample_name, sample in sample_dict.items():
                fasta = path.join(seq_dir, sample['sample_name'], sample['fasta'])
                sample['fasta_path'] = fasta

            failed += [x['sample_name'].split('_')[0] for x in csv.DictReader(open(qc_file[0]), dialect=csv.excel)  if x['qc_pass'] == 'FALSE']
        else: 
            logging.error('Only 1 qc file can be used ')
    # Remove controls 
    new_sample_dict = {} 
    for sample_name in sample_dict.keys():
        if not sample_name.endswith('PC') and not sample_name.endswith('NC'):
            new_sample_dict[sample_name] = sample_dict[sample_name]

    sample_dict = new_sample_dict
    for sample_name, sample  in sample_dict.items():
        copy(sample['fasta_path'], path.join(outputdir, sample_name.split('_')[0] + '.fa'))

    

if __name__ == '__main__':
    data_dirs = ['/home/ubuntu/transfer/incoming/QIB_Sequencing/Covid-19_Seq/result.illumina.20210804-Pakistan', '/home/ubuntu/transfer/incoming/QIB_Sequencing/Covid-19_Seq/result.illumina.20210730-Pakistan']
    outputdir = 'temp/fasta'
    main(data_dirs, outputdir)