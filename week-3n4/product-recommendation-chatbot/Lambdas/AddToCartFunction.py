import json
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
cart_table = dynamodb.Table('workshop-Cart-1PXY88CM648O1')
table = dynamodb.Table('product_work')

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
    product_name = query_params.get('productName')

    if not user_id or not product_name:
        responseBody = {
            "application/json": {
                "body": json.dumps('Missing required parameters: userId and productName')
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
    try:
        # Get the input product details from the Products table
        input_product = table.get_item(Key={'product_name': product_name}).get('Item')
        
        print(json.dumps(input_product))
        
        if not input_product:
            responseBody = {
                "application/json": {
                    "body": json.dumps('input product not found in Products Table')
                }
            }
        
            action_response = {
                'actionGroup': actionGroup,
                'apiPath': apiPath,
                'httpMethod': httpMethod,
                'httpStatusCode': 400,
                'responseBody': responseBody
            }
    
            api_response = {'response': action_response, 'messageVersion': event['messageVersion']}
            print("Response: {}".format(api_response))
            return api_response
            
        # Check if the item already exists in the cart
        response = cart_table.get_item(
            Key={
                'user_id': user_id,
                'product_name': product_name
            }
        )

        if 'Item' not in response:
            # Add the item to the cart
            cart_table.put_item(
                Item={
                    'user_id': user_id,
                    'product_name': product_name
                }
            )
            responseBody = {
                "application/json": {
                    "body": json.dumps(f'Product "{product_name}" added to cart for user "{user_id}"')
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
        else:
            responseBody = {
                "application/json": {
                    "body": json.dumps(f'Product "{product_name}" already in cart for user "{user_id}"')
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
    except ClientError as e:
        error_message = e.response['Error']['Message']
        print(error_message)
        responseBody = {
            "application/json": {
                "body": json.dumps(f'Error: {error_message}')
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
