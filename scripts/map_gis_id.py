import csv

HEADERS = ["Accession_ID", "submitter", "fn","covv_virus_name","covv_type","covv_passage","covv_collection_date","covv_location","covv_add_location","covv_host","covv_add_host_info","covv_sampling_strategy","covv_gender","covv_patient_age","covv_patient_status",	"covv_specimen",	"covv_outbreak",	"covv_last_vaccinated",	"covv_treatment",	"covv_seq_technology",	"covv_assembly_method",	"covv_coverage",	"covv_orig_lab",	"covv_orig_lab_addr",	"covv_provider_sample_id",	"covv_subm_lab",	"covv_subm_lab_addr",	"covv_subm_sample_id",	"covv_authors"] 

mapping = {k['Virus name']: k['Accession ID'] for k in csv.DictReader(open('temp/pak_gis_id'), dialect=csv.excel_tab()) } 
new_records = [] 
for x in csv.DictReader(open('gisaidsubout/gisaidsub.csv')):
    x['Accession_ID'] = mapping[x['covv_virus_name']]
    new_records.append(x)

out = csv.DictWriter(open('gisaidsubout/gisaidsub_with_ids.csv', 'w'), fieldnames=HEADERS)
out.writeheader()
out.writerows(new_records)

