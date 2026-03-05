import json
import boto3
from botocore.exceptions import ClientError
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('product_work')


def lambda_handler(event, context):
    """ function to get data from Products table """
    try:
        if parameters := event.get('parameters'):
            # Normalize gender values
            gender_mapping = {
                "male": "men",
                "female": "women",
                "boy": "men",
                "girl": "women",
                "man": "men",
                "woman": "women"
            }
            for param in parameters:
                if param['name'] == 'gender':
                    param['value'] = gender_mapping.get(param['value'].lower(), param['value'].lower())
            
            # Build the filter expression based on the provided query parameters
            filter_expression = " AND ".join([f"#{param['name']} = :{param['name']}" for param in parameters])
            expression_attribute_values = {f":{param['name']}":param['value'] for param in parameters}
            expression_attribute_names = {f"#{param['name']}":param['name'] for param in parameters}
            # Retrieve products of the DynamoDB table, first results page only limited to 100 items
            response = table.scan(
                FilterExpression=filter_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                Limit=100
                )
        else:
            # In case no filters the Retrieve all products of the DynamoDB table, first results page only limited to 100 items
            response = table.scan(Limit=100)
        products = response['Items']
        action_response = {
            'actionGroup': event['actionGroup'],
            'apiPath': event['apiPath'],
            'httpMethod': event['httpMethod'],
            'httpStatusCode': 200,
            'responseBody': {
                "application/json": {
                    "body": json.dumps(products)
                }
            }
        }
        api_response = {'response': action_response, 'messageVersion': event['messageVersion']}
        print(f"Response: {api_response}")
        return api_response
    except ClientError as e:
        error_response = {
            'actionGroupName': 'Get-Product-Recommendations',
            'apiPath': '/products',
            'httpMethod': 'GET',
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
        api_error_response = {'response': error_response, 'messageVersion': '1.0'}
        print(f"Response: {api_error_response}")
        return api_error_response
    except Exception as e:
        error_response = {
            'actionGroupName': 'Get-Product-Recommendations',
            'apiPath': '/products',
            'httpMethod': 'GET',
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
        api_error_response = {'response': error_response, 'messageVersion': '1.0'}
        print(f"Response: {api_error_response}")
        return api_error_response
