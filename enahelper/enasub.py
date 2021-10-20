"""
enasub uploads data to ENA via the ena webcli

Requires ena web cli program 

### CHANGE LOG ### 
2020-12-03 Nabil-Fareed Alikhan <nabil@happykhan.com>
    * Initial build - split from dirty scripts
"""
import time 
import argparse
import meta
import logging
import xml.etree.ElementTree as ET
from enautil import startup, get_samples
import yaml
from os import path, mkdir
import shutil
from copy import deepcopy 
import sys 
from enaschema import GISENAMeta
from marshmallow import EXCLUDE
import csv
from enautil import load_yaml, format_meta
import requests 
import gzip
from Bio import SeqIO

epi = "Licence: " + meta.__licence__ +  " by " +meta.__author__ + " <" +meta.__author_email__ + ">"
logging.basicConfig()
log = logging.getLogger()


def create_sub(config, prefix, output_dir, template='templates/template_sub.xml'): 
    sub_xml = prefix + "-sub.xml"
    sub_xml_path = path.join(output_dir, sub_xml)
    shutil.copy(template, sub_xml_path)
    tree = ET.parse(sub_xml_path)
    root = tree.getroot()
    root.set('broker_name', config['broker'])
    root.set('center_name', config['center_name'])
    with open(sub_xml_path, 'wb') as out: 
        out.write(ET.tostring(root))        
    return sub_xml, sub_xml_path 

def create_project(args, template='templates/template_project.xml'):
    log.info('Create Project')
    output_dir, server, config = startup(args.tempdir, args.real)
    project_meta = yaml.load(open(args.metadata), Loader=yaml.FullLoader)
    
    sub_xml, sub_xml_path = create_sub(config, args.prefix, output_dir)
    project_xml = args.prefix + "-project.xml"
    project_xml_path = path.join(output_dir, project_xml)
    shutil.copy(template, project_xml_path)    

    tree = ET.parse(project_xml_path)
    root = tree.getroot()
    root.find('PROJECT').set('broker_name', config['broker'])
    root.find('PROJECT').set('center_name', config['center_name'])    
    root.find('PROJECT').set('alias', 'enasubproj-' + project_meta['alias'])    
    root.find('PROJECT').find('TITLE').text = project_meta['title']
    root.find('PROJECT').find('DESCRIPTION').text = project_meta['description']
    with open(project_xml_path, 'wb') as out: 
        out.write(ET.tostring(root))       

    submission_dict = {
            "SUBMISSION": (sub_xml, open(sub_xml_path, 'r'), 'application/x-www-form-urlencoded'),
            "PROJECT": (project_xml, open(project_xml_path, 'r'), 'application/x-www-form-urlencoded')
        }
    requests.post(server, auth=(config['user'],config['passwd']), files= submission_dict)


def create_samples(args, template='templates/template_sample.xml'):
    output_dir, server, config = startup(args.tempdir, args.real)
    sub_xml, sub_xml_path = create_sub(config, args.prefix, output_dir)
    samples = get_samples(args.file_info)

    custom_fields = load_yaml(args.field_mappings)
    global_values = load_yaml(args.global_values)

    meta = format_meta(list(samples.keys()), args.metadata, global_values=global_values, custom_fields=custom_fields)

    samples_xml = args.prefix + "-samples.xml"
    samples_xml_path = path.join(output_dir, samples_xml)
    shutil.copy(template, samples_xml_path)    

    
    # Create XML 
    tree = ET.parse(samples_xml_path)
    root = tree.getroot()
    root.find('SAMPLE').set('broker_name', config['broker'])
    root.find('SAMPLE').set('center_name', config['center_name'])    
    new_sample = deepcopy(root.find('SAMPLE'))
    sample = root.find('SAMPLE')
    count = 1
    for record in meta:
        log.info(f'Adding {record["isolate"]}')
        sample.set('alias', record['isolate'].replace('/', '_'))
        sample.find('TITLE').text = f"{record['scientific_name']} {record['isolate']}"
        sample.find('SAMPLE_NAME').find('TAXON_ID').text = record['tax_id']
        sample.find('SAMPLE_NAME').find('SCIENTIFIC_NAME').text = record['scientific_name']
        attr_list  = sample.find('SAMPLE_ATTRIBUTES')
        for key, value in GISENAMeta(unknown = EXCLUDE).dump(record).items():
            new_attr = ET.SubElement(attr_list, 'SAMPLE_ATTRIBUTE')
            new_tag = ET.SubElement(new_attr, 'TAG')
            new_tag.text = key
            new_value = ET.SubElement(new_attr, 'VALUE')
            new_value.text = value
            if key == 'host age':
                new_unit  = ET.SubElement(new_attr, 'UNITS')
                new_unit.text = 'years'                
        if count < len(samples.keys()):
            sample = deepcopy(new_sample)
            root.append(sample)
            count += 1 

    with open(samples_xml_path, 'wb') as out: 
        out.write(ET.tostring(root))           
    submission_dict = {
            "SUBMISSION": (sub_xml, open(sub_xml_path, 'r'), 'application/x-www-form-urlencoded'),
            "SAMPLE": (samples_xml, open(samples_xml_path, 'r'), 'application/x-www-form-urlencoded')
        }
    info = requests.post(server, auth=(config['user'],config['passwd']), files= submission_dict)             
    print(info.text)


def submit_data(args):
    output_dir, server, config = startup(args.tempdir, args.real)
    mani_in_path = path.join(output_dir, 'mani_in')
    if not path.exists(mani_in_path):
        mkdir(mani_in_path)    
    samples = get_samples(args.file_info)        
    submission_script_path = path.join(output_dir, 'read-submission.sh')
    submission_script_out = open(submission_script_path, 'w')
    ass_submission_script_path = path.join(output_dir, 'ass-submission.sh')
    ass_submission_script_out = open(ass_submission_script_path, 'w')

    data_meta = load_yaml(args.global_values)

    acc = {x['alias']: x for x in  csv.DictReader(open(args.datameta), dialect=csv.excel) }
    # Ok need to add some duplicate records to handle weird sample names    
    new_acc = {} 
    for alias, x in acc.items(): 
        # hCoV-19_Lebanon_QIB-862_2021
        if alias.startswith('hCoV-19_Lebanon') or alias.startswith('hCoV-19_Pakistan') :
            new_acc[alias.split('_')[2]] = x 
    acc.update(new_acc)
    submit = '' 
    if args.real:
        submit = ' -submit '
    for sample_name, sample in samples.items():
        safe_name = sample_name
        mani_file = path.join(mani_in_path , f'{safe_name}.mani.txt')
        if not acc.get(sample_name.replace('/', '_')):
            continue
        this_acc = acc[sample_name.replace('/', '_')]['id']    

        with open(mani_file, 'w') as man:
            man.write(f'STUDY {args.study}\n')
            man.write(f'SAMPLE {this_acc}\n')
            man.write(f'NAME {args.runname} surveillance {sample_name}\n')
            man.write(f'INSERT_SIZE {data_meta["insert_size"]}\n')
            man.write(f'INSTRUMENT {data_meta["instrument"]}\n')
            man.write(f'LIBRARY_STRATEGY {data_meta["library_strategy"]}\n')
            man.write(f'LIBRARY_SOURCE {data_meta["library_source"]}\n')
            man.write(f'LIBRARY_SELECTION {data_meta["library_selection"]}\n')
            man.write(f'BAM {sample["bam"]}\n')

        submission_script_out.write(f"java -jar bin/webin-cli-4.1.0.jar  -manifest={mani_file}  {submit} -userName={config['user']} -context=reads -passwordFile=pass  -validate  -centername=\"{config['center_name']}\" -inputdir={path.dirname(sample['bam_path'])}\n")


        if path.exists(sample["fasta_path"]): 
            mani_file = path.join(mani_in_path , f'{safe_name}-ass.mani.txt')
            f_in = open(sample["fasta_path"], 'rb')
            fasta_zip = sample["fasta_path"] + '.gz'
            fasta_zip_name = sample["fasta"] + '.gz'
            f_out = gzip.open(fasta_zip, 'w')
            f_out.writelines(f_in)
            f_out.close()
            f_in.close()
            chr_file = path.join(path.dirname(sample['fasta_path']) , f'{safe_name}-ass.chr.gz')     
            chr_file_name =  f'{safe_name}-ass.chr.gz'             
            with open(mani_file, 'w') as man:
                man.write(f'STUDY {args.study}\n')
                man.write(f'SAMPLE {this_acc}\n')
                man.write(f'ASSEMBLYNAME {args.runname} {safe_name}\n')
                man.write(f'ASSEMBLY_TYPE COVID-19 outbreak\n')
                man.write(f'COVERAGE 100\n')
                man.write(f'PROGRAM {data_meta["assembly_program"]}\n')
                man.write(f'PLATFORM {data_meta["platform"]}\n')
                man.write(f'FASTA {fasta_zip_name}\n')
                man.write(f'CHROMOSOME_LIST {chr_file_name}\n')
            for record in SeqIO.parse(sample["fasta_path"], "fasta"):
                chr_name = (record.id)
            with gzip.open(chr_file, 'wb') as f_out:
                exy = f'{chr_name}\t1\tChromosome\n'
                f_out.write(exy.encode('utf_8'))
            f_out.close()

            ass_submission_script_out.write(f"java -jar bin/webin-cli-4.1.0.jar  {submit} -manifest={mani_file}   -userName=\"{config['user']}\" -context=genome -passwordFile=pass  -validate  -centername=\"{config['center_name']}\" -inputdir={path.dirname(sample['fasta_path'])}\n")




if __name__ == '__main__':
    start_time = time.time()
    log.setLevel(logging.INFO)
    desc = __doc__.split('\n\n')[0].strip()
    parser = argparse.ArgumentParser(description=desc,epilog=epi)
    subparsers = parser.add_subparsers(help='commands')
    parser.add_argument ('-v', '--verbose', action='store_true', default=False, help='verbose output')
    parser.add_argument('--version', action='version', version='%(prog)s ' + meta.__version__)
    parser.add_argument('--tempdir', action='store', default='enasubdir', help='Temp dir for output xml files' )
    parser.add_argument('--prefix', action='store', default='mysub', help='Prefix for output xml' )
    parser.add_argument('--real', action='store_true', default=True, help='Submit to ENA for real, sends to test server by default' )

    # Create project 
    project_parser = subparsers.add_parser('create_project', help='Create project for ENA submission')
    project_parser.add_argument('--metadata', action='store', help='Project Metadata', default='project_meta.yaml')
    project_parser.set_defaults(func=create_project)

    # Create samples 
    sample_parser = subparsers.add_parser('create_samples', help='Create XML for submission')
    sample_parser.add_argument('metadata', action='store', help='Sample Metadata')
    sample_parser.add_argument('file_info', action='store', help='Sample File info')
    sample_parser.add_argument('--field_mappings', action='store', default='scripts/ena-sample-map.yaml', help='field mappings YAML')     
    sample_parser.add_argument('--global_values', action='store', default='scripts/ena-globals.yaml', help='global values YAML')
    sample_parser.set_defaults(func=create_samples)

    # Submit data
    data_parser = subparsers.add_parser('create_data_sub', help='Prepare read data and library info')
    data_parser.add_argument('file_info', action='store', help='Table including sample file paths')
    data_parser.add_argument('runname', action='store', help='Run Name')
    data_parser.add_argument('study', action='store', help='Study reference')
    data_parser.add_argument('datameta', action='store', help='Metadata')
    data_parser.add_argument('--submit', action='store_true', help='Submit to ENA, validates by default')
    data_parser.add_argument('--global_values', action='store', default='scripts/ena-globals.yaml', help='global values YAML')
    data_parser.set_defaults(func=submit_data)

    args = parser.parse_args()
    if args.verbose: 
        log.setLevel(logging.DEBUG)
        log.debug( "Executing @ %s\n"  %time.asctime())    
    if hasattr(args, 'func'):
        args.func(args)
    else: 
        parser.print_help()
    if args.verbose: 
        log.debug("Ended @ %s\n"  %time.asctime())
        log.debug('total time in minutes: %d\n' %((time.time() - start_time) / 60.0))
    sys.exit(0)