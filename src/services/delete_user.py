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
        # Delete the user from the DynamoDB table
        table.delete_item(Key={'id': user_id})
    except ClientError as e:
        print(e.response['Error']['Message'])
        return {
            'statusCode': 500,
            'body': json.dumps({"message": 'An error occurred when deleting the item from DynamoDB'})
        }

    # If the item was deleted successfully, return a 200 OK status code and a success message
    return {
        'statusCode': 200,
        'body': json.dumps({"message": f"User with ID {user_id} deleted successfully"}),
    }
