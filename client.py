import requests
import base64

# URL of API gateway
url                     = "https://ooa60ku0pj.execute-api.ap-southeast-1.amazonaws.com/prod"
url_uploadDownload      = url + "/upload-download"
url_viewObject          = url + "/viewobject"
url_shareObject         = url + "/shareobject"
url_signup              = url + "/signup"
url_login               = url + "/login"
# username and password for login
username = None
password = None

# show welcome text.
def showWelcome():
    print("Welcome to MyDropbox Application")
    print("====================================================================")
    print("Please input command (newuser USERNAME password PASSWORD, login")
    print("USERNAME PASSWORD, put FILENAME, get FILENAME, view, or logout).")
    print("If you want to quit the program just type quit.")
    print("====================================================================")

# upload file by sending POST request that attach file and username/filename to endpoint /upload-download .
def upload(filepath):
    global username
    try:
        # open file that want to upload.
        files= {'upload_file': open(filepath,'rb') }
    except:
        print('file not found on your local machine!')
    # attach username and filename in the request
    data = {}
    data['username'] = username
    data['filename'] = filepath

    try:
        # send POST request.
        r = requests.post(url_uploadDownload, files = files, data=data).json()
        print(r)
    except:
        print("[Client failed] There is somethings wrong! please try again.")

# download files/objects by sending GET request that attach username/filename to endpoint /upload-download.
def download(username, filename, fileOwner):
    # attach username and filename in the request
    data = {}
    data["username"] = username
    data["filename"] = filename
    data["fileOwner"] = fileOwner

    r = None

    try :
        # GET request
        r = requests.get(url_uploadDownload, data=data).json()
        # BASE64 decode file
        data = base64.b64decode(r["Body"][1:])
        # save file
        file = open(filename, "wb")
        file.write(data)
        file.close()
        print("OK")
    except :
        if r is None:
            print("[Client failed] There is somethings wrong! please try again.")
        else: print(r)

# view object by sending GET request that attach username to endpoint /viewobject.
def viewObject():
    # using global declare username (username that user login)
    global username
    # attach username in the request
    data = {}
    data['username'] = username
    try:
        # send GET request.
        responses = requests.get(url_viewObject, data=data).json()
        for item in responses:
            owner = item['owner']
            contentLength = item['contentLength']
            filename = item['path'].split('/')[1]
            lastModified = item['lastModified']
            print(filename, contentLength, lastModified, owner)

    except:
        print("[Client failed] There is something wrong! please try again.")

# share object by sending POST request that attach username, filename and targetUser to endpoint /shareobject.
def shareobject(filename, targetUser):
    # using global declare username (username that user login)
    global username
    data = {}
    data['username'] = username
    data['filename'] = filename
    data['targetUser'] = targetUser

    try:
        # send POST request to endpoint /shareobject.
        responses = requests.post(url_shareObject, data=data).json()
        print(responses)
    except:
        print("[Client failed] There is something wrong! please try again.")

def signup(username, password):
    data = {}
    data['username'] = username
    data['password'] = password
    try:
        # send POST request to endpoint /signup.
        responses = requests.post(url_signup, data=data).json()
        print(responses)
    except:
        print("[Client failed] There is something wrong! please try again.")

def login(login_username, login_password):
    global username, password
    data = {}
    data['login_username'] = login_username
    data['login_password'] = login_password
    try:
        # send POST request to endpoint /login.
        responses = requests.post(url_login, data=data)
        statusCode = responses.status_code
        if statusCode == 200 and responses.json() == "OK":
            username = login_username
            password = login_password
        print(responses.json())
    except:
        print("[Client failed] There is something wrong! please try again.")



def init():
    global username, password
    showWelcome()

    while True:
        print(">>> ", end="")
        userInput = str(input()).split()
        if ''.join(userInput) == 'quit': break

        elif userInput[0] == "login":
            if len(userInput) == 3:
                login_username = userInput[1]
                login_password = userInput[2]
                login(login_username, login_password)
            else:
                print("please input 'login [YOUR_EMAIL] [YOUR PASSWORD]'")
        
        elif userInput[0] == "newuser":
            if len(userInput) == 4:
                username = userInput[1]
                password = userInput[3]
                signup(username, password)
            else:
                print("please input 'newuser [EMAIL] password [PASSWORD]'")

        elif username != None:
            if userInput[0] == "put":
                if len(userInput) == 2:
                    filename = userInput[1]
                    upload(filename)
                else:
                    print("please input 'put [FILE_PATH]'")

            elif userInput[0] == "get":
                if len(userInput) == 3:
                    filename = userInput[1]
                    fileOwner = userInput[2]
                    download(username, filename, fileOwner)

                else:
                    print("please input 'get [FILENAME] [OWNER_EMAIL]'")

            elif userInput[0] == "share":
                if len(userInput) == 3:
                    filename = userInput[1]
                    targetUser = userInput[2]
                    shareobject(filename, targetUser)
                else:
                    print("please input 'share [FILENAME] [TARGET_USER]'")
        
            elif userInput[0] == "view":
                viewObject()

            elif userInput[0] == "whoami":
                print(username)

            elif userInput[0] == "logout":
                if len(userInput) == 1:
                    username = None
                    password = None
                    print("OK")
                else:
                    print("please input 'logout'")

            else:
                print("unknown command.")

        else:
            print("Please login!")
        
init()