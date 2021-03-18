from flask import Flask, send_file , request, jsonify
from flasgger import Swagger, swag_from
from Functions.epwProcess import mainEPW
from Functions.obxmlProcess import mainObxml
from Functions.idfProcess import mainIdf
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

template = {
  "swagger": "2.0",
  "info": {
    "title": "BIMERR REST",
    "description": "API to transform files to json format.",
    "contact": {
      "responsibleOrganization": "https://oeg.fi.upm.es//",
      "responsibleDeveloper": "https://github.com/Salva5297",
      "email": "salvador.gonzalez.gerpe@upm.es",
      "url": "https://github.com/Salva5297/file2json_bimerr",
    },
    "termsOfService": "http://me.com/terms", # apache
    "version": "0.0.1"
  },
  "host": "weather.bimerr.iot.linkeddata.es",  # overrides localhost:500
  "basePath": "",  # base bash for blueprint registration
  "schemes": [
    "https"
  ],
  "operationId": "getmyData"
}

swagger = Swagger(app, template=template)


class Bimerr():
    @app.route('/epw', methods=["POST"])
    @swag_from('../yamls/epw.yml')
    def post_epw():
        if(request.files["EpwFile"]):
            file = request.files["EpwFile"]
            file.save(os.path.join("tmp/", secure_filename(file.filename)))
            file_stats = os.stat("tmp/"+file.filename)

            json_file = mainEPW("tmp/"+file.filename)

            os.remove("tmp/"+file.filename)

        return jsonify(json_file)


    @app.route('/obxml', methods=["POST"])
    @swag_from('../yamls/obxml.yml')
    def post_obxml():
        if(request.files["ObxmlFile"]):
            file = request.files["ObxmlFile"]
            file.save(os.path.join("tmp/", secure_filename(file.filename)))

            file_stats = os.stat("tmp/"+file.filename)

            json_file,nameFile = mainObxml("tmp/"+file.filename)

            os.remove(nameFile.replace('.xml','.json'))

        return jsonify(json_file)

    
    @app.route('/idf', methods=["POST"])
    @swag_from('../yamls/idf.yml')
    def post_idf():
        if(request.files["IdfFile"]):
            file = request.files["IdfFile"]
            file.save(os.path.join("tmp/", secure_filename(file.filename)))

            file_stats = os.stat("tmp/"+file.filename)

            json_file = mainIdf("tmp/"+file.filename)

            os.remove("tmp/"+file.filename)

        return jsonify(json_file)



app.run(host='0.0.0.0')