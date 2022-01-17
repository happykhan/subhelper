from os import path, listdir, mkdir
import logging 
import csv 
from shutil import copy

logging.basicConfig(level=logging.DEBUG)

# Fetch valid sample names and paths 
def main(data_dirs, outputdir, good):
   
    sample_dict = {}
    failed = []  
    headers = [] 
    for data_dir in data_dirs:
        qc_file = [path.join(data_dir, x) for x in listdir(data_dir) if x.endswith('.qc.csv')] 
        if len(qc_file) == 1:
            files = path.join(data_dir, 'qc_climb_upload')
            seq_dir = path.join(files, listdir(files)[0])
            new_sample_dict = {'UHS2-' + x['sample_name'].split('_')[0] : x for x in csv.DictReader(open(qc_file[0]), dialect=csv.excel)  if 'UHS2-' + x['sample_name'].split('_')[0] in good }
            for sample_name, sample in new_sample_dict.items():
                bam_path = path.join(seq_dir, sample['sample_name'], sample['bam']) 
                if not path.exists(bam_path):
                    new_bam = sample['sample_name'] + '.mapped.bam' 
                    sample['bam'] = new_bam
                    bam_path = path.join(seq_dir, sample['sample_name'], new_bam) 
                    if not path.exists(bam_path):
                        print('Does not exists path ' + bam_path)
                sample['bam_path'] = bam_path
                sample['fasta_path'] = path.join(seq_dir, sample['sample_name'], sample['fasta'])
                sample['sample_id'] = sample_name.split('_')[0]
                sample['lab_id'] = sample['sample_name'].split('_')[0]
                headers = list(sample.keys())
            sample_dict.update(new_sample_dict)
            failed += [x['sample_name'].split('_')[0] for x in csv.DictReader(open(qc_file[0]), dialect=csv.excel)  if x['qc_pass'] == 'FALSE']
        else: 
            logging.error('Only 1 qc file can be used ')
    # Remove controls 
    new_sample_dict = {} 
    for sample_name in sample_dict.keys():
        if not sample_name.endswith('PC') and not sample_name.endswith('NC'):
            new_sample_dict[sample_name] = sample_dict[sample_name]
        
    sample_dict = new_sample_dict
    outout = csv.DictWriter(open(outputdir, 'w'), fieldnames=headers) 
    outout.writeheader()
    outout.writerows(list(sample_dict.values()))
    

if __name__ == '__main__':
    data_dirs = ['/home/ubuntu/transfer/incoming/QIB_Sequencing/Covid-19_Seq/result.illumina.20210804-Pakistan', '/home/ubuntu/transfer/incoming/QIB_Sequencing/Covid-19_Seq/result.illumina.20210730-Pakistan']

    outputdir = 'temp/pak-sub/file_locs.csv'
    gis_sub = 'temp/pak-sub/pak.gis.csv'
    submitted = [x['covv_virus_name'].split('/')[2] for x in csv.DictReader(open(gis_sub), dialect=csv.excel())] 
    
    # good = {'QIB-' + x['#']: x['NIC ID'] for x in csv.DictReader(open('temp/leb-sub/mapping'), dialect=csv.excel_tab()) if 'QIB-' + x['#'] in submitted } 
    good = submitted 
    main(data_dirs, outputdir, good)