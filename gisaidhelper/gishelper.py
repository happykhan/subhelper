from Bio import SeqIO 
from openpyxl import Workbook, load_workbook
import textwrap
import yaml
import csv
from gisaidschema import Gismeta, HEADERS
from marshmallow import EXCLUDE
import json
from os import path

def merge_fasta_dir(input_paths, sample_map, output_file):
    all_fasta = [] 
    for sample_name, fasta_path in input_paths.items():
        rec = SeqIO.parse(open(fasta_path), 'fasta')
        sample_name = sample_map[sample_name.split('.')[0]]
        for fas in rec:
            fas.id = sample_name
            fas.decription = '' 
            fas.name = '' 
            all_fasta.append(fas)
    with open(output_file, "w") as output_handle:
        for x in all_fasta:
            output_handle.write(f'>{x.id}\n')
            seq = textwrap.fill(str(x.seq))
            output_handle.write(f'{seq}\n')
    return output_file

def load_yaml(file_path):
    with open(file_path) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        return data

def format_table(sample_names, sheet_location, file_output, custom_fields=None, global_values=None):
    all_records = [] 
    sample_map = {}
    for record in csv.DictReader(open(sheet_location), dialect=csv.excel_tab()):
        record['fn'] = file_output
        if custom_fields:
            inv_custom_fields = {v: k for k, v in custom_fields.items()}
            for old_key, right_key in inv_custom_fields.items():
                if record.get(old_key):
                    record[right_key] = record[old_key]
                    record.pop(old_key)
        if record['sample_name'] in sample_names:
            old_sample_name = record['sample_name']
            
            if global_values:
                record.update(global_values)
                record['sample_name'] = record['sample_prefix'] + record['sample_name'] 
            record['covv_virus_name'] = f"hCoV-19/{record['country']}/{record['sample_name']}/2021"
            record['covv_location'] = f"{record['continent']}/{record['country']}/{record['covv_location']}"
            clean_record = Gismeta(unknown = EXCLUDE).load(record)
            clean_record = json.loads(json.dumps(clean_record, default=str))
            all_records.append(clean_record)        
            sample_map[old_sample_name] = record['covv_virus_name']
    return all_records, sample_map

def write_table(metadata, outputdir):
    meta_out_path = path.join(outputdir, 'gisaidsub.csv')
    meta_out = csv.DictWriter(open(meta_out_path, 'w'), fieldnames=HEADERS, dialect=csv.excel())
    meta_out.writeheader()
    meta_out.writerows(metadata)    