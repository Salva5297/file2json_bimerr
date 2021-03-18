import glob
import os
import json
import logging
from pyidf.idf import IDF

def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

def mainIdf(file):
    # Obtenemos el contenido de cada uno de los ficheros pertenecientes al formato de IDF
    logging.info("start")
    idfContent = IDF(file)

    # Creamos el diccionario que se va a introducir en el fichero JSON
    dictionary = {}
    dictionary['Elements'] = [] ##


    # Por cada elemento existente dentro del contenido del IDF, almacenamos su información dentro de un mini diccionario y posteriormente lo incorporamos al diccionario original
    for elem in idfContent:
        attribute = {} ##
        attribute['Name'] = elem.schema['pyname'].replace(' ', '_') ##
        inList = []
        for item in elem.items():
            inList.append(item[0])

        if any("Layer" in s for s in inList):
            attribute['Type'] = "Layer"
        else:
            attribute['Type'] = "Material"

        attribute['PropertyValuePair'] = []
        name = ''
        for item in elem.items():
            if item[0] == "Name" or item[0] == "Material Name":
                name = item[1].replace(".)", ')').replace(': ', '_').replace(' ', '_').replace('.', "'").replace('/', '_')
                attribute['MatName'] = name
                attribute['MatNameStr'] = item[1]
                                            
            else:
                miniDic = {}
                miniDic["ComplexName"] = name + '__' + str(item[0]).replace(' ', '_')
                miniDic["Name"] = str(item[0]).replace(' ', '_')

                data = str(item[0]).lower()
                try:
                    miniDic["Unit"] = elem.schema['fields'][data]['unit']
                except:
                    pass

                if elem.schema['fields'][data]['type'] == 'alpha':
                    miniDic['Datatype'] = 'string'
                elif elem.schema['fields'][data]['type'] == 'real':
                    miniDic['Datatype'] = 'float'
                else:
                    pass

                if str(item[1]).replace(' ', '_') != "None":
                    if is_number(item[1]):
                        miniDic["Value"] = item[1]
                    else:
                        miniDic["Value"] = str(item[1]).replace(' ', '_')
                else:
                    miniDic["Value"] = None
                attribute["PropertyValuePair"].append(miniDic)

        
        dictionary['Elements'].append(attribute)
        


    return dictionary