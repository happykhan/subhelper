from marshmallow import Schema, fields, post_dump, pre_load, validate


class ENAMeta(Schema):
    central_sample_id = fields.Str()
    tax_id = fields.Str(missing='2697049') 
    scientific_name = fields.Str(missing='Severe acute respiratory syndrome coronavirus 2')
    sample_title = fields.Str()
    sample_description = fields.Str()
    collection_date = fields.Str()
    country = fields.Str(missing='United Kingdom')
    region = fields.Str()
    capture = fields.Str(missing='active surveillance in response to outbreak')
    host = fields.Str(missing='Human')
    source_age = fields.Integer()
    host_health_state = fields.Str(missing='not provided')
    source_sex = fields.Str(validate=validate.OneOf(['male', 'female']))
    host_scientific_name = fields.Str(missing='Homo sapiens')
    collector_name = fields.Str(missing="Justin O'Grady")
    collecting_org = fields.Str( missing="Quadram Institute Bioscience")
 
    @pre_load
    def clean_up(self, in_data, **kwargs):
        for k,v in dict(in_data).items():
            if v in [''] :
                in_data.pop(k)        
            elif isinstance(v, str):
                in_data[k] = v.strip()
        if in_data.get('source_sex'):
            if in_data['source_sex'] == 'M':
                in_data['source_sex'] = 'male'
            if in_data['source_sex'] == 'F':
                in_data['source_sex'] = 'female'
        if in_data.get("adm2"):
            in_data["region"] = in_data.get("adm2")
            in_data.pop('adm2')
        return in_data

    @post_dump
    def wash(self, in_data, **kwargs):
        for k,v in dict(in_data).items():
            if k in ['scientific_name', 'tax_id'] :
                in_data.pop(k)         
        if in_data.get("country"):
            in_data["geographic location (country and/or sea)"] = in_data["country"]
        in_data.pop('country')
        if in_data.get('adm2'):
            in_data["geographic location (region and locality)"] = in_data["adm2"]
            in_data.pop('adm2')        
        in_data["sample capture status"] = in_data["capture"]
        in_data.pop('capture')                
        in_data["host common name"] = in_data["host"]
        in_data.pop('host')     
        if in_data.get("source_age"):
            in_data["host age"] = str(in_data["source_age"])
            in_data.pop('source_age')
        if in_data.get("source_sex"):                            
            in_data["host sex"] = in_data["source_sex"]
            in_data.pop('source_sex')
        else:
            in_data["host sex"] = 'not provided'                                 
        in_data['host subject id'] = in_data['central_sample_id']
        in_data['isolate'] = in_data['central_sample_id']
        in_data.pop('central_sample_id')
        in_data['collecting institution'] = in_data['collecting_org']
        in_data.pop('collecting_org')
        in_data['collector name'] = in_data['collector_name']
        in_data.pop("collector_name")
        in_data['host health state'] = in_data['host_health_state']
        in_data.pop("host_health_state")
        in_data['host scientific name'] = in_data['host_scientific_name']
        in_data.pop("host_scientific_name")        
        in_data['ENA-CHECKLIST'] = 'ERC000033'
        return in_data



class GISENAMeta(Schema):
    isolate = fields.Str()
    tax_id = fields.Str(missing='2697049') 
    scientific_name = fields.Str(missing='Severe acute respiratory syndrome coronavirus 2')
    sample_title = fields.Str()
    sample_description = fields.Str()
    collection_date = fields.Str()
    country = fields.Str(missing='United Kingdom')
    region = fields.Str()
    capture = fields.Str(missing='active surveillance in response to outbreak')
    host = fields.Str(missing='Human')
    source_age = fields.Integer()
    host_health_state = fields.Str(missing='not provided')
    source_sex = fields.Str(validate=validate.OneOf(['male', 'female', 'not provided']))
    host_scientific_name = fields.Str(missing='Homo sapiens')
    collector_name = fields.Str()
    collecting_org = fields.Str( missing="Quadram Institute Bioscience")
 
    @pre_load
    def clean_up(self, in_data, **kwargs):
        for k,v in dict(in_data).items():
            if v in ['', 'unknown'] :
                in_data.pop(k)        
            elif isinstance(v, str):
                in_data[k] = v.strip()
        if in_data.get('source_sex'):
            if in_data['source_sex'].lower() == 'male':
                in_data['source_sex'] = 'male'
            if in_data['source_sex'].lower() == 'female':
                in_data['source_sex'] = 'female'
        if in_data.get("Location"):
            in_data["region"] = in_data.get("Location").split('/')[2]
            in_data["country"] = in_data.get("Location").split('/')[1]
            in_data.pop('Location')
        if in_data.get("Collection date"):            
            in_data['collection_date'] = in_data.get("Collection date")
        if in_data.get("Virus name"):
            in_data['isolate'] = in_data.get("Virus name")
   #     if in_data.get("Patient status"):
   #         in_data['host_health_state'] = in_data.get("Patient status")            
        if in_data.get("Patient age"):
            if in_data.get("Patient age").isdigit():
                in_data['source_age'] = in_data.get("Patient age")                       
        if in_data.get("Originating lab"):
            in_data['collecting_org'] = in_data.get("Originating lab")                       
        if in_data.get("Authors"):
            in_data['collector_name'] = in_data.get("Authors").split(',')[0]
        return in_data

    @post_dump
    def wash(self, in_data, **kwargs):
        for k,v in dict(in_data).items():
            if k in ['scientific_name', 'tax_id'] :
                in_data.pop(k)         
        if in_data.get("country"):
            in_data["geographic location (country and/or sea)"] = in_data["country"]
        in_data.pop('country')        
        in_data["sample capture status"] = in_data["capture"]
        in_data.pop('capture')                
        in_data["host common name"] = in_data["host"]
        in_data.pop('host')     
        if in_data.get("source_age"):
            in_data["host age"] = str(in_data["source_age"])
            in_data.pop('source_age')
        if in_data.get("source_sex"):                            
            in_data["host sex"] = in_data["source_sex"]
            in_data.pop('source_sex')
        else:
            in_data["host sex"] = 'not provided'                                 
        in_data['host subject id'] = in_data['isolate']
        in_data['collecting institution'] = in_data['collecting_org']
        in_data.pop('collecting_org')
        in_data['collector name'] = in_data['collector_name']
        in_data.pop("collector_name")
        in_data['host health state'] = in_data['host_health_state']
        in_data.pop("host_health_state")
        in_data['host scientific name'] = in_data['host_scientific_name']
        in_data.pop("host_scientific_name")        
        in_data['ENA-CHECKLIST'] = 'ERC000033'
        return in_data        

if __name__ == '__main__':   
    import csv  
    from marshmallow import EXCLUDE

    for x in csv.DictReader(open('temp/PAK')):
        print(GISENAMeta(unknown = EXCLUDE).load(x) )
