import json

def lambda_handler(event, context):
    print(json.dumps(event))