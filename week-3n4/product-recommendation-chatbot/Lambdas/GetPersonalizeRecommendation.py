import json
import boto3
import random
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('product_work')

def lambda_handler(event, context):
    try:
        agent = event['agent']
        actionGroup = event['actionGroup']
        apiPath = event['apiPath']
        httpMethod = event['httpMethod']
        parameters = event.get('parameters', [])
        requestBody = event.get('requestBody', {})
    
        query_params = {}
        for param in parameters:
            query_params[param['name']] = param['value']
    
        # Extract the input product name (item ID) from the query parameters
        input_product_name = query_params.get('product_name')
        
        print(json.dumps(event))
    
        if not input_product_name:
            responseBody = {
                "application/json": {
                    "body": json.dumps('Missing input product name (item ID)')
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
    
        # Get the input product details from the Products table
        input_product = table.get_item(Key={'product_name': input_product_name}).get('Item')
        
        print(json.dumps(input_product))
        
        if not input_product:
            responseBody = {
                "application/json": {
                    "body": json.dumps('input product not found')
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
    
        # Extract the occasion and gender from the input product
        input_occasion = input_product.get('occasion')
        input_gender = input_product.get('gender')
    
        # Scan the Products table to get all products
        response = table.scan()
        products = response.get('Items', [])
    
        # If the Products table is empty, return an empty list
        if not products:
            recommended_product = []
        else:
            # Filter out the input product and products that don't match the input occasion and gender
            recommended_products = [
                product for product in products
                if product['product_name'] != input_product_name
                and product.get('occasion') == input_occasion
                and product.get('gender') == input_gender
            ]
            
            
    
            # If there are no other products, return an empty list
            if not recommended_products:
                recommended_product = []
            else:
                # Select a random product from the list of recommended products
                recommended_product = [random.choice(recommended_products)]
    
        responseBody = {
            "application/json": {
                "body": json.dumps(recommended_product)
            }
        }
    
        action_response = {
            'actionGroup': actionGroup,
            'apiPath': apiPath,
            'httpMethod': httpMethod,
            'httpStatusCode': 200,
            'responseBody': responseBody
        }
    
        api_response = {'response': action_response, 'messageVersion': event['messageVersion']}
        print("Response: {}".format(api_response))
        return api_response
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
