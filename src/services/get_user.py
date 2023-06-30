import json
import boto3
from botocore.exceptions import ClientError

# Create a DynamoDB resource
dynamodb = boto3.resource('dynamodb')


def lambda_handler(event, context):
    # Extract the user ID from the path parameters
    user_id = event["pathParameters"]["id"]

    # Validate the user ID
    if not user_id:
        return {
            'statusCode': 400,
            'body': json.dumps({"message": "id is required"})
        }

    table = dynamodb.Table('AkaUsers')

    try:
        # Get the user details from the DynamoDB table
        response = table.get_item(Key={'id': user_id})
    except ClientError as e:
        print(e.response['Error']['Message'])
        return {
            'statusCode': 500,
            'body': json.dumps({"message": 'An error occurred when retrieving the item from DynamoDB'})
        }

    # If the item was retrieved successfully, return a 200 OK status code and the user details
    if 'Item' in response:
        user = response['Item']
        return {
            'statusCode': 200,
            'body': json.dumps({
                'id': user['id'],
                'firstName': user['firstName'],
                'lastName': user['lastName'],
                'email': user['email'],
                # In a real-world application, NEVER return passwords in the response
            }),
        }
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({"message": "User not found"}),
        }
