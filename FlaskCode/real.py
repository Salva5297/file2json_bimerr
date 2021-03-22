from flask import Flask, send_file, request, jsonify
from flasgger import Swagger, swag_from
from Functions.epwProcess import mainEPW
from Functions.obxmlProcess import mainObxml
from Functions.idfProcess import mainIdf
from Functions.getEPWYears import mainGetEpwYears
from Functions.getEPWFiles import mainDownloadEPW
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

template = {  # apache
              # overrides localhost:5000
              # base bash for blueprint registration
    'swagger': '2.0',
    'info': {
        'title': 'BIMERR REST',
        'description': 'API to transform files to json format.',
        'contact': {
            'responsibleOrganizaticon': 'https://oeg.fi.upm.es/',
            'responsibleDeveloper': 'https://github.com/Salva5297',
            'email': 'salvador.gonzalez.gerpe@upm.es',
            'url': 'https://github.com/Salva5297/file2json_bimerr',
            },
        'termsOfService': 'https://github.com/Salva5297/file2json_bimerr/blob/master/LICENSE',
        'version': '0.0.1',
        },
    'host': '',
    'basePath': '',
    'schemes': ['https'],
    } # Add http to try it at local

swagger = Swagger(app, template=template)


class Bimerr:
    
    @app.route('/epw', methods=['POST'])
    @swag_from('../yamls/epw.yml')
    def post_epw():
        if request.files['EpwFile']:
            file = request.files['EpwFile']
            file.save(os.path.join('tmp/',secure_filename(file.filename)))
                      
            file_stats = os.stat('tmp/' + file.filename)
            
            json_file = mainEPW('tmp/' + file.filename)
            
            os.remove('tmp/' + file.filename)
            
        return jsonify(json_file)
        
    @app.route('/obxml', methods=['POST'])
    @swag_from('../yamls/obxml.yml')
    def post_obxml():
        if request.files['ObxmlFile']:
            file = request.files['ObxmlFile']
            file.save(os.path.join('tmp/',secure_filename(file.filename)))
                      
            file_stats = os.stat('tmp/' + file.filename)
            
            (json_file, nameFile) = mainObxml('tmp/' + file.filename)
            
            os.remove(nameFile.replace('.xml', '.json'))
            
        return jsonify(json_file)
        
    @app.route('/idf', methods=['POST'])
    @swag_from('../yamls/idf.yml')
    def post_idf():
        if request.files['IdfFile']:
            file = request.files['IdfFile']
            file.save(os.path.join('tmp/',secure_filename(file.filename)))
            file_stats = os.stat('tmp/' + file.filename)
            json_file = mainIdf('tmp/' + file.filename)
            os.remove('tmp/' + file.filename)
        return jsonify(json_file)
        
        
    @app.route('/getEpwYears', methods=['POST'])
    @swag_from('../yamls/getEPWYears.yml')
    def post_getEpwYears():
        json_data = request.json
        listYears = mainGetEpwYears(json_data)
        listYears = ','.join(listYears)
        dictionary = {'years': listYears}
        return jsonify(dictionary)
    
    @app.route('/getEPWData', methods=['POST'])
    @swag_from('../yamls/downloadEPW.yml')
    def post_downloadEPW():
        json_data = request.json
        dictionary = mainDownloadEPW(json_data)
        return jsonify(dictionary)


app.run(host='0.0.0.0', port=8000)
