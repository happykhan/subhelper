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