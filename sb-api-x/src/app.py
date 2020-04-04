# app.py is the main entry-point for the Chalice framework
# Chalice Framework documentation can be found at: https://chalice.readthedocs.io/en/latest/

from chalice import Chalice
import json

app = Chalice(app_name='chalice-app')
app.debug = True

@app.route('/permissions')
def permissionsConfiguration():
    # dummy function to generate IAM role permissions through Chalice magic
    import boto3
    boto3.client('dynamodb').get_item()
    boto3.client('dynamodb').put_item()
    boto3.client('dynamodb').query()
    boto3.client('s3').put_object()

@app.route('/animal', cors = True)
def animalApi():
    from chalicelib import sb_get
    response = sb_get.get_animal(app.current_request.query_params.get('Id'))
    return json.dumps({'request': str(app.current_request.query_params), 'response': response })

@app.route('/search', cors = True)
def searchApi():
    from chalicelib import sb_search
    qp = app.current_request.query_params
    response = sb_search.query(qp['StatusCategory'], 
            qp['AnimalType'] if type(qp['AnimalType']) is list else [qp['AnimalType']], 
            qp['Location'] if type(qp['Location']) is list else [qp['Location']])
    return json.dumps({'request': str(qp), 'response': response })
    
@app.route('/webhook', methods=['POST', 'GET'], content_types = ['application/x-www-form-urlencoded', 'application/json'])
def webhookApi():
    from chalicelib import sb_webhook
    event = app.current_request.to_dict()
    event["body"] = json.dumps(app.current_request.json_body)
    return sb_webhook.handler(event)

@app.schedule('rate(5 minutes)')
def syncScheduler(event):
    from chalicelib import sb_sync
    sb_sync.sync()
