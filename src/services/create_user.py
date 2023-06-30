import json
import boto3
import uuid
from botocore.exceptions import ClientError

# Create a DynamoDB resource
dynamodb = boto3.resource('dynamodb')


# Data validation function
def validate_user_data(user):
    if not user.get("firstName"):
        return "firstName is required"
    if not user.get("lastName"):
        return "lastName is required"
    if not user.get("email"):
        return "email is required"
    if not user.get("password"):
        return "password is required"
    # Add any other data validation rules you might have
    return None


def lambda_handler(event, context):
    # Parse the body of the request
    body = json.loads(event["body"])

    # Validate the user data
    error = validate_user_data(body)
    if error:
        return {
            'statusCode': 400,
            'body': json.dumps({"message": error})
        }

    # Extract the user details
    first_name = body.get("firstName")
    last_name = body.get("lastName")
    email = body.get("email")
    password = body.get("password")  # Please remember to hash passwords before storing!

    # Generate a unique id for the new user
    id = str(uuid.uuid4())

    table = dynamodb.Table('AkaUsers')

    try:
        # Put the user details into the DynamoDB table
        table.put_item(Item={
            'id': id,
            'firstName': first_name,
            'lastName': last_name,
            'email': email,
            'password': password  # In a real-world application, NEVER store plaintext passwords
        })
    except ClientError as e:
        print(e.response['Error']['Message'])
        return {
            'statusCode': 500,
            'body': json.dumps({"message": 'An error occurred when inserting the item into DynamoDB'})
        }

    # If the item was inserted successfully, return a 201 Created status code and the user details
    return {
        'statusCode': 201,
        'body': json.dumps({
            'id': id,
            'firstName': first_name,
            'lastName': last_name,
            'email': email,
            # In a real-world application, NEVER return passwords in the response
        }),
    }
