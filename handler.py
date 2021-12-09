import urllib3 
import json
import boto3
import datetime
from datetime import datetime, timezone
import os 
from time import sleep

## AWS Users
usernames = []
## AWS User expirkeys
expirkeys = [] 
## AWS User password_lifetime
pwlifetimes =[]
## Expir trem 
expir = 90

def awsauth():
    ## Change an other Role
    sts_connection = boto3.client('sts')
    acct_b = sts_connection.assume_role(
        RoleArn="arn:aws:iam::{controltowerID}:role/{managementControltowerIamControlRole}",
        RoleSessionName="cross-iam-control-access"
    )
    
    ACCESS_KEY = acct_b['Credentials']['AccessKeyId']
    SECRET_KEY = acct_b['Credentials']['SecretAccessKey']
    SESSION_TOKEN = acct_b['Credentials']['SessionToken']

    # create service client using the assumed role credentials, e.g. iam
    iam = boto3.client(
        'iam',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        aws_session_token=SESSION_TOKEN,
    )

## Mamangement IAM Auth
iam = boto3.client('iam')
##awsauth()

def checkAccesskey():
    ## make IAM User list
    users = iam.list_users()
    for user in users['Users']:
        tmp = str(user['UserName'])
        usernames.append(tmp)
    
    ## make expir accesskey list(and check acive accesskey)
    for username in usernames:
        ## except iam user
        if username == "user01" or username == "user02" or username == "user03":
            pass
        else:
            accesskeys = iam.list_access_keys(UserName = username)
            for accesskey in accesskeys['AccessKeyMetadata']:
                status = accesskey['Status']
                ## (now - createdate)days
                activeday = (datetime.now(timezone.utc)-accesskey['CreateDate']).days
                ## Active and over expir date
                if status == "Active" and activeday > expir:
                    result = [username,activeday,accesskey['AccessKeyId']]
                    expirkeys.append(result)
    return expirkeys

def generateCredentialReport():
    response = iam.generate_credential_report()
    print(response)

def checkPasswdLifetime():
    generateCredentialReport()
    sleep(10)
    report = iam.get_credential_report()
    table = report["Content"]
    table = str(table).split("\\n")
    #head = table[0]
    table = table[1:]

    today = datetime.now()
    #print(head)
    for row in table:
        column = row.split(",")
        user = column[0]
        # arn = column[1]
        # user_creation_time = column[2]
        password_enabled = column[3]
        try:
            password_next_rotation = datetime.strptime(column[6], "%Y-%m-%dT%H:%M:%S+00:00")
        except:
            password_next_rotation = today
            pass

        activeday = (password_next_rotation.replace(tzinfo=None) - datetime.now()).days

        password_lifetime = 90 - int(activeday) -1
        
        if password_enabled == "true" and password_lifetime > expir :
            result=[user,password_lifetime,password_next_rotation]
            #print("User: "+ user +" | ARN: "+ arn +" | User Creation Time: "+ user_creation_time + " | Password Enabled: "+ password_enabled +" | Password Next Rotation: " + str(password_next_rotation) +" | password lifetime: "+ str(password_lifetime))
            if user == "backend-rc" or user == "jenkins-cdn" or user == "dev-monitoring-iam" or user == "mz-admin" or user == "randomuser":
                pass
            else: 
                pwlifetimes.append(result)
    return pwlifetimes

def upload_file_s3(bucket, file_name, file):
    encode_file = bytes(json.dumps(file).encode('UTF-8'))
    s3 = boto3.client('s3')
    try:
        s3.put_object(Bucket=bucket, Key=file_name, Body=encode_file)
        return True
    except:
        return False

http = urllib3.PoolManager() 
def handler(event, context): 

    ## Dooray webhook URL
    #url = "https://hook.dooray.com/services/*************************************"
    url = os.environ['dooraywebhookurl']

    headers = {
        'Content-type':'application/json', 
        'Accept':'application/json'
    }
  
    userlist = ""
    ck_result = checkAccesskey()
    count = "Expir Accesskey Count: " + str(len(ck_result))
    for ekey in ck_result:
        expirkeyuser = ekey[0:1][0]
        activeday = str(ekey[1:2][0])
        userlist += "IAMUser: "+expirkeyuser+" | Accesskey Active day("+activeday+")\n"
    print(userlist)

    userpwlifetimelist = ""
    ck_result2 = checkPasswdLifetime()
    count2 = "Expir Password Count: " + str(len(ck_result2))
    for upwlifetime in ck_result2:
        expirpasswduser = upwlifetime[0:1][0]
        passwdlifetime = upwlifetime[1:2][0]
        passwdnextrotation = upwlifetime[2:3][0]
        userpwlifetimelist += "IAMUser: "+expirpasswduser+" | PasswordLifeTime("+ str(passwdlifetime) +") | Password Next Rotation: "+ str(passwdnextrotation) +"\n"
    print(userpwlifetimelist)

    text = "schedule(UTC): "+str(datetime.now(timezone.utc))
      
    msg =  {
        "botName": "AWS Bot", 
        "botIconImage": "https://static.dooray.com/static_images/dooray-bot.png", 
        "text": text,
        "attachments" : [
            {
                "title" : "Expir Password used IAMUser Count",
                "text" : count2,
                "color" : "red"
            },
            {
                "title" : "Expir Password used IAMUser List",
                "text" : userpwlifetimelist,
                "color" : "red"
            },
            {
                "title" : "Expir Accesskey Count",
                "text" : count,
                "color" : "red"
            },
            {
                "title" : "Expir Accesskey used IAMUser List",
                "text" : userlist,
                "color" : "red"
            },
            {
                "title" : "Reoport Link",
                "titleLink" : "{URL}",
                "text" : "List of IAMUsers who used Passwd & accessKey for 90 days",
                "color" : "red"
            }
        ]
    }
  
    encoded_msg = json.dumps(msg).encode('utf-8')
    resp = http.request('POST',url, headers=headers, body=encoded_msg)
    
    print(resp)

    #bucket = 'ui-mobile-publish.dev-nsmall.com' #당신의 버킷 이름
    #file_name = "grmoon/20210929"
    #file = json.loads(ck_result)
    
    #result = upload_file_s3(bucket, file_name + '.html', ck_result)

    #if result:
    #    return {
    #        'statusCode': 200,
    #        'body': json.dumps("upload success")
    #    }
    #else:
    #    return {
    #        'statusCode': 400,
    #        'body': json.dumps("upload fail")
    #    }

