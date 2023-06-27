import uuid
import boto3
import json
import os
from botocore.exceptions import ClientError

# Instantiate AWS SDK clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    try:
        # Parse operation and callbackUrl from event body
        body = json.loads(event['body'])
        operation = body['operation']
        callback_url = body['callbackUrl']
        file_content = body['fileContent']  # This should be the base64-encoded content of the file

        # Generate a unique ID for the batch (you may use a different logic for this)
        batch_id = str(uuid.uuid4())

        # Upload the file to S3
        s3_client.put_object(
            Body=file_content,
            Bucket="user-bulk-operations-data",
            Key=batch_id + '.csv'  # We are assuming the file is a CSV file
        )

        # Store the operation type and callback URL in DynamoDB
        table = dynamodb.Table("BulkUsersManagementTable")
        table.put_item(
            Item={
                'BatchId': batch_id,
                'Operation': operation,
                'CallbackUrl': callback_url,
                'Status': 'PENDING'
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps('CSV file uploaded and batch operation started')
        }

    except ClientError as e:
        print(e.response['Error']['Message'])
        return {
            'statusCode': 500,
            'body': json.dumps('An error occurred while processing the request')
        }
