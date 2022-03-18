import json
import boto3
from boto3.dynamodb.conditions import Key
import urllib.parse
from urllib.parse import unquote
import base64

# s3
s3_resource = boto3.resource('s3')
s3_client = boto3.client('s3')
bucketName = "nasri-dropbox"
my_bucket = s3_resource.Bucket(bucketName)

# dynamoDB
objectsTableName = "myDropbox-objects"
authTableName = "myDropbox-auth"
dynamodb = boto3.resource('dynamodb')
objectsTable = dynamodb.Table(objectsTableName)
authTable = dynamodb.Table(authTableName)

# set variables
vieopbjectPath      = "viewobject"
viewobjectPath      = "/viewobject"
sharePath           = "/shareobject"
getMethod           = "GET"
postMethod          = "POST"


def lambda_handler(event, context):
    path = event["path"]
    httpMethod = event["httpMethod"]
    body = unquote( event["body"] )

    if path == viewobjectPath and httpMethod == getMethod:
        try:
            username = body.split("&")[0].split("=")[1]
        except:
            return buildResponse(400, body="Invalid request!")
            
        return viewobject(username)
        
    if path == sharePath and httpMethod == postMethod:
        try:
            username    = body.split("&")[0].split("=")[1]
            filename    = body.split("&")[1].split("=")[1]
            targetUser  = body.split("&")[2].split("=")[1]
            objectName  = "{}/{}".format(username, filename)
        except:
            return buildResponse(400, body="Invalid request!")
            
        return shareobject(username, objectName, targetUser)
        
    return buildResponse(404, body="Not Found! (Incorrect endpoint or httpMethod)")

# view object.        
def viewobject(username):
    
    objects = []
    objectName = "ken/testscript.txt"
    try:
        # get object/file from S3 bucket with username prefix filtering 
        response = objectsTable.query(KeyConditionExpression=Key('username').eq(username))
        return buildResponse(200, body=response['Items'])

    except:
        return buildResponse(400, body="There is something wrong with the process of getting object from AWS S3! please try again.")
        
def shareobject(username, objectName, targetUser):
    try:
        # check if target exist.
        findtarget = authTable.query(KeyConditionExpression=Key('username').eq(targetUser))
        if len( findtarget['Items'] ) == 0:
            return buildResponse(404, body="target user not found!")
           
        # get metadata of file (file that user want to share)
        fileMetadata = objectsTable.get_item(Key = {'username': username, 'path': objectName})
        if 'Item' not in fileMetadata:
            return buildResponse(404, body="Your file doesn't exist!")
        
        fileMetadata = fileMetadata['Item']
        objectsTable.put_item(Item = {
                'username': targetUser,
                'path': fileMetadata['path'],
                'lastModified': fileMetadata['lastModified'],
                'contentLength': fileMetadata['contentLength'],
                'owner': fileMetadata['owner']
            })
        #response = objectsTable.get_item(Key = {'username': username, 'path': objectName})
        return buildResponse(200, body="OK")
    except:
        return buildResponse(400, body="dynamoDB fail!")
        
def buildResponse(statusCode, body=None):
    response = {
        'statusCode': statusCode
    }
    
    if body is not None:
        response['body'] = json.dumps(body)
        
    return response
    