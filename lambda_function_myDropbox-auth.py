import json
import boto3
from urllib.parse import unquote

# dynamoDB
authTableName = "myDropbox-auth"
dynamodb = boto3.resource('dynamodb')
authTable = dynamodb.Table(authTableName)

# set variables
loginPath = "/login"
signupPath = "/signup"
postMethod = "POST"

def lambda_handler(event, context):
    # API-gateway resource
    path = event["path"]
    httpMethod = event["httpMethod"]
    body = unquote( event["body"] )
    
    try:
        # the format of body will be like "username=nasri&password=qwerty"
        username = body.split("&")[0].split("=")[1]
        password = body.split("&")[1].split("=")[1]
    except:
        return buildResponse(400, body="Invalid request!")
    
    if path == loginPath and httpMethod == postMethod:
        return login(username, password)
    
    if path == signupPath and httpMethod == postMethod: 
        return signup(username, password)
        
    return buildResponse(404, body="Not Found! (Incorrect endpoint or httpMethod)")

# function login - in order to login, check is the username and password match in the database.
def login(username, password):
    try:
        # check are username and password match in the database
        response = authTable.get_item(Key = {'username': username})
        if 'Item' in response:
            real_password = response['Item']['password']
            if password == real_password:
                return buildResponse(200, body="OK")
        
        # if no username found in the database. return 400
        return buildResponse(400, body="Incorrect username or password!")
        
    except:
        return buildResponse(404, body="Not Found!")

# function signup - check is username already exist in the database, if not add username and password in the database.
def signup(username, password):
    try:
        # check if username already exist in the database.
        response = authTable.get_item(Key = {'username': username})
        if 'Item' in response:
            return buildResponse(200, body="username already exist!")
            
        # if not, add new username, password. in the myDropbox-auth table
        authTable.put_item(Item = {
            'username': username,
            'password': password
        })
        
        return buildResponse(200, body="signup sucess")
    
    except:
        return buildResponse(404, body="Not Found!")
        
def buildResponse(statusCode, body=None):
    response = {
        'statusCode': statusCode
    }
    
    if body is not None:
        response['body'] = json.dumps(body)
        
    return response
        