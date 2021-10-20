
from os import path, mkdir
import yaml
import csv 
from enaschema import GISENAMeta
from marshmallow import EXCLUDE
import json 

def startup(tempdir, real, config_file='scripts/enaconfig.yaml'): 
    if not path.exists(tempdir):
        mkdir(tempdir)
    if real:
        server = "https://www.ebi.ac.uk/ena/submit/drop-box/submit"
    else:
        server = "https://wwwdev.ebi.ac.uk/ena/submit/drop-box/submit"
    config = yaml.load(open(config_file), Loader=yaml.FullLoader)
    return tempdir, server, config
    

def get_samples(file_loc):
    return {x['sample_name']: x for x in  csv.DictReader(open(file_loc))}

def format_meta(sample_list, sheet_location, global_values=None, custom_fields=None):
    all_records = [] 
    if sheet_location.endswith('.csv'):
        csv_records = csv.DictReader(open(sheet_location), dialect=csv.excel())
    else:
        csv_records = csv.DictReader(open(sheet_location), dialect=csv.excel_tab())
    for record in csv_records:
        if custom_fields:
            for old_key, right_key in custom_fields.items():
                if record.get(old_key):
                    record[right_key] = record[old_key]
                    record.pop(old_key)
        if record['isolate'].split('/')[2] in sample_list:
            if global_values:
                record.update(global_values)
    
            record['country'] = record['covv_location'].split('/')[1].strip()
            clean_record = GISENAMeta(unknown = EXCLUDE).load(record)
            clean_record = json.loads(json.dumps(clean_record, default=str))
            all_records.append(clean_record)        
    return all_records

def load_yaml(file_path):
    with open(file_path) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        return data
