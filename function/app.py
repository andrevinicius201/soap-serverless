'''
Created on Feb 21, 2023

@author: ctelles
'''
import json
import boto3
import urllib3
import os
import base64
from _io import StringIO
from saxonche import *

class PayloadTransformerException(Exception):
    pass

session= boto3.Session()
s3 = session.resource('s3')
proc = PySaxonProcessor(license=False)
xsltproc = proc.new_xslt30_processor()
http = urllib3.PoolManager()
PARAM_BODY = None
PARAM_REQUEST_PAYLOAD = None
PARAM_RESPONSE_PAYLOAD = None
PARAM_ENDPOINT = None

def split_s3_path(s3_path):
    path_parts=s3_path.replace("s3://","").split("/")
    bucket=path_parts.pop(0)
    key="/".join(path_parts)
    return bucket, key

def get_xslt(s3_session, s3_xslt):
    try:
        bucket, key = split_s3_path(s3_xslt)
        if bucket == '.':
            return
        else:
            obj = s3_session.Object(bucket,key)
            return obj.get()['Body'].read().decode('utf-8')
    except Exception as error:
        raise PayloadTransformerException('PayloadTransformerException: {}'.format(error))

def call_http_backend(requestJSON, endpoint):
    try:
        encoded_data = json.dumps(requestJSON).encode('utf-8')
        r = http.request(
            'POST',
            endpoint,
            body=encoded_data,
            headers={'Content-Type': 'application/json'}
        )
        return json.loads(r.data.decode('utf-8'))    
    except Exception as error:
        raise PayloadTransformerException('PayloadTransformerException: {}'.format(error))
    
def getInputParameters(event):
    global PARAM_BODY
    global PARAM_REQUEST_PAYLOAD
    global PARAM_RESPONSE_PAYLOAD
    global PARAM_ENDPOINT
    try:
        body = event.get('body')
        if body:
            xsltrq = event.get('xsltrq') 
            xsltrs = event.get('xsltrs') 
            endpoint = event.get('endpoint') 
            if not xsltrq:
                xsltrq = os.getenv('xsltrq')
            if not xsltrs:
                xsltrs = os.getenv('xsltrs')
            if not endpoint:
                endpoint = os.getenv('endpoint')
            PARAM_BODY = body
            PARAM_REQUEST_PAYLOAD = xsltrq
            PARAM_RESPONSE_PAYLOAD =  xsltrs
            PARAM_ENDPOINT = endpoint
        else: 
            request = event['Records'][0]['cf']['request']
            PARAM_BODY = base64.b64decode(request['body']['data']).decode('utf-8')
            origin = str(request['origin']['custom']['domainName'])
            uri = str(request['uri'])
            PARAM_REQUEST_PAYLOAD = './xslt/xml2json.xslt'
            PARAM_RESPONSE_PAYLOAD =  './xslt/json2xml.xslt'
            PARAM_ENDPOINT = 'https://1klopjzia8.execute-api.sa-east-1.amazonaws.com/soap/bargainfinderscenario2'
    except Exception as error:
        raise PayloadTransformerException('PayloadTransformerException: {}'.format(error))
    
def transformPayload (inputPayload, transformationFile):
    try:
        document = proc.parse_xml(xml_text=inputPayload)
        xslt = get_xslt(s3, transformationFile)
        if xslt:
            transformer = xsltproc.compile_stylesheet(stylesheet_text=xslt)
        else:
            transformer = xsltproc.compile_stylesheet(stylesheet_file=transformationFile)
        return transformer.transform_to_string(xdm_node=document)
    except Exception as error:
        raise PayloadTransformerException('PayloadTransformerException: {}'.format(error))   
    
def lambda_handler(event, context):
    try:
        getInputParameters(event)
        requestJSON = StringIO(transformPayload(PARAM_BODY, PARAM_REQUEST_PAYLOAD)).getvalue()
        
        if PARAM_ENDPOINT and PARAM_RESPONSE_PAYLOAD:
            responseJSON = call_http_backend(requestJSON, PARAM_ENDPOINT)
            outputjson = transformPayload('<xml><![CDATA['+json.dumps(responseJSON)+']]></xml>', PARAM_RESPONSE_PAYLOAD)
        else:
            outputjson = requestJSON
    except Exception as error:
        outputjson = error 
    
    resp = {
        'status': '200',
        'statusDescription': 'OK',
        'headers': {
            'cache-control': [
                {
                    'key': 'Cache-Control',
                    'value': 'max-age=100'
                }
            ],
            "content-type": [
                {
                    'key': 'Content-Type',
                    'value': 'application/soap-xml'
                }
            ]
        },
        'body': outputjson
    }
    
    return resp
