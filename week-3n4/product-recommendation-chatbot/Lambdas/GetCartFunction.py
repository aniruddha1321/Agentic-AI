import json
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
cart_table = dynamodb.Table('workshop-Cart-1PXY88CM648O1')

def lambda_handler(event, context):
    agent = event['agent']
    actionGroup = event['actionGroup']
    apiPath = event['apiPath']
    httpMethod = event['httpMethod']
    parameters = event.get('parameters', [])
    query_params = {}
    for param in parameters:
        query_params[param['name']] = param['value']

    user_id = query_params.get('userId')

    if not user_id:
        responseBody = {
            "application/json": {
                "body": json.dumps('Missing required parameter: userId')
            }
        }
        action_response = {
            'actionGroup': actionGroup,
            'apiPath': apiPath,
            'httpMethod': httpMethod,
            'httpStatusCode': 400,
            'responseBody': responseBody
        }
        return {'response': action_response, 'messageVersion': event['messageVersion']}

    # Scan the table to get all items for the user
    response = cart_table.scan(
        FilterExpression=boto3.dynamodb.conditions.Key('user_id').eq(user_id)
    )

    items = response.get('Items', [])
    cart_items = [{'product_name': item['product_name']} for item in items]

    responseBody = {
        "application/json": {
            "body": json.dumps(cart_items)
        }
    }
    action_response = {
        'actionGroup': actionGroup,
        'apiPath': apiPath,
        'httpMethod': httpMethod,
        'httpStatusCode': 200,
        'responseBody': responseBody
    }
    return {'response': action_response, 'messageVersion': event['messageVersion']}
