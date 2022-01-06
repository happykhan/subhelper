# subhelper
helper scripts for submission to ena (microbial + sarscov2) and gisaid (sarscov2 only)

## enahelper

interactive site: https://www.ebi.ac.uk/ena/submit/sra/#home
webin (xml) submission: https://www.ebi.ac.uk/ena/submit/webin/





## gisaidsub USAGE

```
usage: gisaidsub.py [-h] [-v] [--version] [--template TEMPLATE]
                    [--outputdir OUTPUTDIR] [--fasta_output FASTA_OUTPUT]
                    [--field_mappings FIELD_MAPPINGS]
                    [--global_values GLOBAL_VALUES]
                    meta_sheet fasta_dir

gisaidsub prepares files for gisaid sub using the interactive batch
submission.

positional arguments:
  meta_sheet            path to metadata sheet
  fasta_dir             directory of fasta files

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         verbose output
  --version             show program's version number and exit
  --template TEMPLATE   Path to GISAID template
  --outputdir OUTPUTDIR
                        output directory
  --fasta_output FASTA_OUTPUT
                        fasta output filename
  --field_mappings FIELD_MAPPINGS
                        field mappings YAML
  --global_values GLOBAL_VALUES
                        global values YAML

Licence: GPLv3 by Nabil-Fareed Alikhan <nabil@happykhan.com>
```

## gisaidsub explained 

The way the script works is that you first need a directory of all the fasta consensus files in one directory. 

You then need an existing sheet of metadata, usually this is provided to you. 

You then need to make two yaml files, that tell the script rules on what fields map to what. 
First field, is the name that GISAID wants in its table, the second is what its call in your sheet. 
e.g.
```
covv_location: Location
covv_collection_date: Date_of_Collection
covv_gender: Gender
covv_patient_age: Age
sample_name: Sample
```

Then you want to have another yaml file of "globals", values that apply to every record, such as. 
```
sample_prefix: MYSample-
submitter: <Your_gisiad_id>
covv_seq_technology: Illumina
covv_orig_lab: <originating lab>
covv_orig_lab_addr: <originating lab address>
covv_subm_lab: <submitting lab>
covv_subm_lab_addr: <submitting lab address> 
covv_authors: <authors>
country: <country collection>
continent: <continent>
```
You can add in as many of the standard gisaid fields. See gisaidschema or GISAID documentation for what those fields could be. 


You then run gisaidhelper:
```
python gisaidsub.py metadata_they_gave.csv  all_fasta_dir --outputdir my_output  --field_mapping my_first_file.yaml --global_values something_global.yaml  
```

The script then:

* takes you csv input swaps the field names as per the mapping yaml and add in the global info. 
* then it validates it with the gisaidscheme.py and produces a csv for submission. 
* It also goes to the fasta dir and merges the sequences into a single file (this is what gisaid wants) 
* and renames each sequence so it is consistent with the metadata. i.e. changes it to hcov-19/X/X/2021

