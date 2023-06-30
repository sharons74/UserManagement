import csv
import boto3
import os
import json
import uuid
from botocore.exceptions import ClientError

s3 = boto3.client('s3')
sqs = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')


def validate_user(user):
    if 'id' not in user or 'firstName' not in user or 'lastName' not in user or 'email' not in user or 'password' not in user:
        raise ValueError('Invalid user data')


def lambda_handler(event, context):
    for record in event['Records']:
        # Get the object from the event
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        # Remove the '.csv' extension from the key to get the batch ID
        batch_id = os.path.splitext(key)[0]

        # Download the file to /tmp
        s3.download_file(bucket, key, '/tmp/file.csv')

        total = 0

        # Fetch operation and callbackURL from DynamoDB table
        batch_table = dynamodb.Table("AkaBatchOperations")
        batch_item = batch_table.get_item(Key={'BatchId': batch_id})['Item']
        operation = batch_item['Operation']

        with open('/tmp/file.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            for row in reader:
                # Assuming the CSV file has columns in this order: id, firstName, lastName, email, password
                user = {
                    'id': row[0],
                    'firstName': row[1],
                    'lastName': row[2],
                    'email': row[3],
                    'password': row[4]
                }

                try:
                    validate_user(user)

                    # Send the message to SQS
                    sqs.send_message(
                        QueueUrl=os.getenv('SQS_QUEUE_URL'),  # replace with your SQS queue URL
                        MessageBody=json.dumps({
                            'operation': operation,
                            'user': user
                        }),
                        MessageGroupId=batch_id
                    )

                    total += 1
                except ValueError:
                    print('Invalid user data: ' + str(row))

        # Update the batch operation item in DynamoDB
        batch_table.update_item(
            Key={'BatchId': batch_id},
            UpdateExpression='SET Total = :total, Remaining = :remaining',
            ExpressionAttributeValues={
                ':total': total,
                ':remaining': total,
            },
            ReturnValues='ALL_NEW'
        )
