import boto3
import json
import os
from botocore.exceptions import ClientError
import requests

# Instantiate AWS SDK clients
sqs = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table("Users")  

def send_callback(url, data):
    try:
        response = requests.post(url, data=json.dumps(data))
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)

def lambda_handler(event, context):
    for record in event['Records']:
        message = json.loads(record['body'])
        operation = message['operation']
        user = message['user']
        batch_table = dynamodb.Table("BulkUsersManagementTable")

        if operation == 'create':
            # Create the user
            try:
                users_table.put_item(Item=user)
            except ClientError as e:
                print(e.response['Error']['Message'])
                batch_table.update_item(
                    Key={'BatchId': record['attributes']['MessageGroupId']},
                    UpdateExpression='ADD Failed :inc',
                    ExpressionAttributeValues={':inc': 1},
                )
        elif operation == 'update':
            # Update the user
            try:
                users_table.update_item(
                    Key={'id': user['id']},
                    UpdateExpression='SET firstName = :firstName, lastName = :lastName, email = :email, password = :password',
                    ExpressionAttributeValues={
                        ':firstName': user['firstName'],
                        ':lastName': user['lastName'],
                        ':email': user['email'],
                        ':password': user['password'],
                    }
                )
            except ClientError as e:
                print(e.response['Error']['Message'])
                batch_table.update_item(
                    Key={'BatchId': record['attributes']['MessageGroupId']},
                    UpdateExpression='ADD Failed :inc',
                    ExpressionAttributeValues={':inc': 1},
                )
        elif operation == 'delete':
            # Delete the user
            try:
                users_table.delete_item(Key={'id': user['id']})
            except ClientError as e:
                print(e.response['Error']['Message'])
                batch_table.update_item(
                    Key={'BatchId': record['attributes']['MessageGroupId']},
                    UpdateExpression='ADD Failed :inc',
                    ExpressionAttributeValues={':inc': 1},
                )

        # Decrease the remaining counter in DynamoDB
        response = batch_table.update_item(
            Key={'BatchId': record['attributes']['MessageGroupId']},
            UpdateExpression='ADD Remaining :dec',
            ExpressionAttributeValues={':dec': -1},
            ReturnValues='UPDATED_NEW'
        )

        # If the remaining counter has reached zero, send the callback
        if response['Attributes']['Remaining'] == 0:
            batch_item = batch_table.get_item(Key={'BatchId': record['attributes']['MessageGroupId']})['Item']
            send_callback(batch_item['CallbackURL'], {
                'processed': batch_item['Total'] - batch_item['Failed'],
                'failed': batch_item['Failed']
            })

        # Delete the SQS message
        sqs.delete_message(
            QueueUrl=os.getenv('SQS_QUEUE_URL'),  # replace with your SQS queue URL
            ReceiptHandle=record['receiptHandle']
        )
