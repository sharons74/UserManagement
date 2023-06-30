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

    # Parse the body of the request
    body = json.loads(event["body"])

    # Extract the user details
    first_name = body.get("firstName")
    last_name = body.get("lastName")
    email = body.get("email")
    password = body.get("password")  # Please remember to hash passwords before storing!

    table = dynamodb.Table('AkaUsers')

    try:
        # Update the user details in the DynamoDB table
        table.update_item(
            Key={'id': user_id},
            UpdateExpression="set firstName=:f, lastName=:l, email=:e, password=:p",
            ExpressionAttributeValues={
                ':f': first_name,
                ':l': last_name,
                ':e': email,
                ':p': password
            },
            ReturnValues="UPDATED_NEW"
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
        return {
            'statusCode': 500,
            'body': json.dumps({"message": 'An error occurred when updating the item in DynamoDB'})
        }

    # If the item was updated successfully, return a 200 OK status code and the updated user details
    return {
        'statusCode': 200,
        'body': json.dumps({
            'id': user_id,
            'firstName': first_name,
            'lastName': last_name,
            'email': email,
            # In a real-world application, NEVER return passwords in the response
        }),
    }
