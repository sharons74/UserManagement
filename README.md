# User Management and Bulk Operations API

This project provides a RESTful API for a user management system using AWS services. The system supports CRUD operations for individual users and batch operations on user data through a bulk endpoint.

## Application Architecture

The application is implemented using a serverless architecture on AWS. It utilizes AWS Lambda for the business logic, API Gateway for exposing the endpoints, DynamoDB for storage, S3 for storing CSV files for bulk operations, and SQS for asynchronous processing of bulk operations.
All the mentioned services are fully managed and can scale automatically.

## API Endpoints

### Create User - `/users` (POST)

Creates a new user in the system.

**Request:**
```json
{
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@example.com",
  "password": "password"
}
```

### Get User - `/users/{id}` (GET)

Retrieves user information by ID.

**Example:**

`GET /users/123`

**Response:**
```json
{
  "id": "123",
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@example.com"
}
```

### Update User - `/users/{id}` (PUT)

Updates user information by ID.

**Example:**

`PUT /users/123`

**Request:**
```json
{
  "firstName": "Jane",
  "lastName": "Doe",
  "email": "jane.doe@example.com"
}
```

### Delete User - `/users/{id}` (DELETE)

Deletes a user by ID.

**Example:**

`DELETE /users/123`

**Response:**
```json
{
  "message": "User with ID 123 deleted successfully"
}
```

### Bulk Operation - `/users/bulk` (POST)

Performs a bulk operation (create, update, or delete) on user data. The request must include a CSV file with user data and a parameter indicating the type of operation.

**Request:**

The request must be a `multipart/form-data` POST request with the following parts:
- `file`: The CSV file with the user data.
- `operation`: The type of operation (create, update, or delete).
- `callbackUrl`: The URL to call back after the operation is completed.

**Example:**

`POST /users/bulk`

The CSV file might contain:

```
id,firstName,lastName,email,password
123,John,Doe,john.doe@example.com,password
124,Jane,Doe,jane.doe@example.com,password
```

**Note:**

In real-world applications, you should not include passwords in plain text, but hash them before storing. This is just a simple example.

## Setup and Run the Application

Clone the repository:

```
git clone https://github.com/sharons74/UserManagement.git
```

### Prerequisites
1. AWS Account
2. AWS CLI installed and configured
3. AWS SAM CLI installed
4. Python 3.8 installed
5. S3 bucket

### Steps

**Step 1: Install necessary dependencies**

Install them locally to a directory (let's say `my_lambda_function/`) with the `pip` command: 

```bash
pip install --target ./my_lambda_function <library_name>
```

Replace <library_name> with the name of any Python libraries that your Lambda function needs.

**Step 2: Add your code**

Add your Python script (e.g., my_lambda_function.py) to the my_lambda_function/ directory.

**Step 3: Zip your code and dependencies**

Navigate to the directory where your my_lambda_function/ directory is located and run the following command to zip your code and dependencies:

```
zip -r my_lambda_function.zip my_lambda_function/*
```

**Step 4: Upload the deployment package to S3**

Upload the my_lambda_function.zip file to your S3 bucket:

```
aws s3 cp my_lambda_function.zip s3://<your-bucket-name>
```
Replace <your-bucket-name> with the name of your S3 bucket.



## Deployment Process

The application is deployed using AWS SAM which simplifies the process of building and deploying the application. The `template.yaml` file included in the repository describes the application's AWS resources.

Deploy the application using AWS SAM:

```
sam build
sam deploy --guided
```
