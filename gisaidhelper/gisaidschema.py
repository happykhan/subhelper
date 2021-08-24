from marshmallow import fields, Schema, validate, pre_load
import datetime 

HEADERS = ["submitter", "fn","covv_virus_name","covv_type","covv_passage","covv_collection_date","covv_location","covv_add_location","covv_host","covv_add_host_info","covv_sampling_strategy","covv_gender","covv_patient_age","covv_patient_status",	"covv_specimen",	"covv_outbreak",	"covv_last_vaccinated",	"covv_treatment",	"covv_seq_technology",	"covv_assembly_method",	"covv_coverage",	"covv_orig_lab",	"covv_orig_lab_addr",	"covv_provider_sample_id",	"covv_subm_lab",	"covv_subm_lab_addr",	"covv_subm_sample_id",	"covv_authors"] 

class Gismeta(Schema):
    class Meta:
        dateformat = '%Y-%m-%d'

    submitter = fields.Str(required=True)
    fn = fields.Str(required=True)
    covv_virus_name = fields.Str(required=True)
    covv_type = fields.Str(default="betacoronavirus", missing="betacoronavirus")
    covv_passage = fields.Str(default="Original", missing="Original")
    covv_collection_date = fields.Str()
    covv_location = fields.Str(required=True)
    covv_add_location = fields.Str(missing="")
    covv_host = fields.Str(default="Human", missing="Human")
    covv_add_host_info = fields.Str(missing="")
    covv_gender = fields.Str(validate=validate.OneOf(["Male", "Female", "Unknown"]))
    covv_patient_age = fields.Str(missing='unknown', default="unknown")
    covv_patient_status = fields.Str( missing='unknown', default="unknown", validate=validate.OneOf(["Hospitalized", "Released", "Live", "Deceased", "unknown"]))
    covv_specimen = fields.Str(validate=validate.OneOf(["Sputum", "Alveolar lavage fluid", "Oro-pharyngeal swab", "Blood", "Tracheal swab", "Urine", "Stool", "Cloakal swab", "Organ", "Feces", "Other"]))
    covv_outbreak = fields.Str(missing="")
    covv_last_vaccinated = fields.Str(missing="")
    covv_treatment = fields.Str(missing="")
    covv_seq_technology = fields.Str(missing="")
    covv_assembly_method = fields.Str(missing="")
    covv_coverage = fields.Str(missing="")
    covv_orig_lab = fields.Str(required=True)
    covv_orig_lab_addr = fields.Str(required=True)
    covv_provider_sample_id = fields.Str(missing="")
    covv_subm_lab = fields.Str(required=True)
    covv_subm_lab_addr = fields.Str(required=True)
    covv_subm_sample_id = fields.Str(missing="") 
    covv_authors = fields.Str(required=True)

    @pre_load
    def clean_up(self, in_data, **kwargs):
        for k,v in dict(in_data).items():
            if v in ['', 'to check',  '#VALUE!', '-', '/', 'Na' ] :
                in_data.pop(k)               
        return in_data
