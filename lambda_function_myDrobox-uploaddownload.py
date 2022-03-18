import json
import boto3
import urllib.parse
from urllib.parse import unquote
import base64

# s3
bucketName = "nasri-dropbox"
s3_resource = boto3.resource('s3')
s3_client = boto3.client('s3')

# dynamoDB
objectsTableName = "myDropbox-objects"
dynamodb = boto3.resource('dynamodb')
objectsTable = dynamodb.Table(objectsTableName)

def lambda_handler(event, context):

    if event["httpMethod"] == "POST":
        return upload(event)
        
    elif event["httpMethod"] == "GET":
        return download(event)
        
    return buildResponse(404, body="Not Found! (Incorrect endpoint or httpMethod)")
    
def buildResponse(statusCode, body=None):
    response = {
        'statusCode': statusCode
    }
    
    if body is not None:
        response['body'] = json.dumps(body)
        
    return response

# upload object/file to S3 bucket.
def upload(event):
    try:
        # if file is base64 encoded, then decode it. if not do nothing.
        if "isBase64Encoded" in event and event["isBase64Encoded"] == True:
            body = str(base64.b64decode(event['body']))[1:]
            delimeter = '\\r\\n'
        else:
            body = str(event['body'])
            delimeter = '\r\n'
    
        # extract filename, content, username from body part of the request
        filename = body.split(delimeter)[7]
        content = body.split(delimeter)[11]
        username = body.split(delimeter)[3].strip()
        
        # each users have thier own directory for storing thier object/file.
        # So, objectName be like "username/filename"
        objectName = "{}/{}".format(username, filename)
        
    except:
        return buildResponse(400, body="There is something wrong with the format of request! please check your request.")
    
    try :
        
        # store object/file in s3 bucket
        object = s3_resource.Object(bucketName, objectName)
        object.put(Body=content)
        
        # get metadata from s3 for updating metadata in dynamoDB.
        metadata = s3_client.head_object(Bucket=bucketName, Key=objectName)
        lastModified = metadata['ResponseMetadata']['HTTPHeaders']['last-modified']
        contentLength = metadata['ResponseMetadata']['HTTPHeaders']['content-length']
        
        # put or update metadata in dynamoDB.
        response = objectsTable.get_item(Key = {'username': username, 'path': objectName})
        
        # update item, if item already exist in dynamoDB
        if 'Item' in response:
            x = objectsTable.update_item(
                    Key={
                        'username': username,
                        'path': objectName,
                    },
                    UpdateExpression="set lastModified=:l, contentLength=:c",
                    ExpressionAttributeValues={
                        ':l': lastModified,
                        ':c': contentLength
                    },
                    ReturnValues="UPDATED_NEW"
                )
            
        else:
            objectsTable.put_item(Item = {
                'username': username,
                'path': objectName,
                'lastModified': lastModified,
                'contentLength': contentLength,
                'owner': username
            })
        
        
        return buildResponse(200, body="OK")
        
        
    except:
        return buildResponse(400, body="There is something wrong with the process of uploading file! please check your command.")
        
# downlaod file from S3 bucket
def download(event):
    try:
        # extract username, filename form GET request
        body = unquote(event["body"]).split("&")
        if len(body) != 3: return { 'statusCode': 400, 'body': json.dumps("invalid request! please check parameter if your request") }
        username = body[0].split("=")[1]
        filename = body[1].split("=")[1]
        fileOwner = body[2].split("=")[1]
        
        # each users have thier own directory for storing thier object/file.
        # So, objectName be like "username/filename"
        objectName = "{}/{}".format(fileOwner, filename)
        
    except:
        return buildResponse(400, body="There is something wrong with the format of your request! please check your request.")
    
    try:
        # check permission in dynamoDB.
        response = objectsTable.get_item(Key = {'username': username, 'path': objectName})
        
        if 'Item' not in response:
            return buildResponse(400, body="File doesn't exist or you don't have permission!")
        
        response = response['Item']
        filepath = response['path']
        
        # get object from S3 bucket then base64 decode content before send to client.
        response = s3_client.get_object(Bucket=bucketName, Key=objectName)
        response["Body"] = base64.b64encode(response["Body"].read())
        return {
            'statusCode': 200,
            'body': json.dumps(response, default=str)
        }
        
    except:
        return buildResponse(400, body="There is something wrong with the process of downloading file! please check your command.")
        
