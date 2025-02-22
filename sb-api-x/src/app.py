# app.py is the main entry-point for the Chalice framework
# Chalice Framework documentation can be found at: https://chalice.readthedocs.io/en/latest/

from chalice import Chalice
import json
from chalicelib.shelterbuddy import DecimalEncoder
import boto3

app = Chalice(app_name='chalice-app')
app.debug = True

@app.route('/permissions')
def permissionsConfiguration():
    # dummy function to generate IAM role permissions through Chalice magic
    import boto3
    boto3.client('dynamodb').get_item()
    boto3.client('dynamodb').put_item()
    boto3.client('dynamodb').query()
    boto3.client('dynamodb').scan()
    boto3.client('dynamodb').delete_item()
    boto3.client('s3').put_object()
    boto3.client('sqs').send_message()
    boto3.client('sqs').receive_message()
    boto3.client('sqs').delete_message()
    boto3.client('sqs').get_queue_attributes()

@app.route('/animal', cors = True)
def animalApi():
    from chalicelib import sb_get
    response = sb_get.get_animal(app.current_request.query_params.get('Id'))
    return json.dumps({'request': str(app.current_request.query_params), 'response': response })

@app.route('/search', cors = True)
def searchApi():
    from chalicelib import sb_search
    qp = app.current_request.query_params
    response = sb_search.query(qp['StatusCategory'], qp.getlist('AnimalType'), qp.getlist('Location'))
    jsonOut = json.dumps({'request': str(qp), 'response': response })
    print(jsonOut)
    return jsonOut

@app.route('/webhook', methods=['POST', 'GET'], content_types = ['application/x-www-form-urlencoded', 'application/json'])
def webhookApi():
    from chalicelib import sb_webhook
    event = app.current_request.to_dict()
    event["body"] = json.dumps(app.current_request.json_body, cls=DecimalEncoder)
    return sb_webhook.intake(event)

@app.schedule('rate(5 minutes)')
def syncScheduler(event):
    from chalicelib import sb_sync
    sb_sync.sync()

@app.on_sqs_message(queue='incomingQueue', batch_size=10)
def incomingAnimal(event):
    try:
        sqs = boto3.client('sqs')
        queue = sqs.get_queue_url(QueueName='incomingQueue')['QueueUrl'] 
        from chalicelib import sb_incoming
        print("Event: ", event.to_dict())
        for record in event:
            animal = json.loads(record.body)
            sb_incoming.process(animal)
            response = sqs.delete_message(QueueUrl=queue, ReceiptHandle=record.receipt_handle)
            print('deleted: ', response)
    except Exception as e:
        print('failed')
        raise(e)

@app.schedule('rate(15 minutes)')
def audit(event):
    from chalicelib import sb_audit
    sb_audit.audit()
