import requests
import json
import sys
import base64

def registerClient( targetURL, clientName, redirectURIs):
    headers = { 'content-type': "application/json"}
    #payload = "{ \"token_endpoint_auth_method\": \"client_credentials\", \"grant_type\" : \"client_credentials\", \"client_name\": \"" + clientName + "\", \"redirect_uris\" : ["
    payload = "{ \"client_name\": \"" + clientName + "\", \"redirect_uris\" : ["
    for uri in redirectURIs:
        payload += "\"" + uri.strip() + "\", "
    payload = payload[:-2]
    payload += "]}"
    res = requests.post(targetURL, data=payload, headers=headers, verify=False)
    print(res)
    matrix = res.json()
    print(matrix)
    print(matrix['grant_types'])
    return (matrix)

def getAccessToken( token_endpoint, credentials, redirectURIs):
    headers = { 'content-type': "application/x-www-form-urlencoded", 'Authorization' : credentials }
    #headers = { 'content-type': "application/x-www-form-urlencoded" }
    payload = {'grant_type' : 'client_credentials'}
    #payload = {'grant_type' : 'authorization_code'}

    res = requests.post(token_endpoint, headers=headers, data=payload, verify=False)
    matrix = res.json()
    #print(matrix)
    return matrix['access_token']
    #return matrix

def createCredentials( client_id, client_secret):
    message = client_id + ':' + client_secret
    #print(message)
    message_bytes = message.encode('utf-8')
    #print(message_bytes)
    base64_bytes = base64.b64encode(message_bytes)
    #print(base64_bytes)
    base64_message = base64_bytes.decode('utf-8')
    #print(base64_message)
    credentials = 'Basic ' + base64_message
    return credentials

def createBearerToken( token):
    return 'Bearer ' + token

def getUserInum(userID, scimUserEndpoint, token):
    headers = { 'content-type': "application/x-www-form-urlencoded", 'Authorization' : createBearerToken(token) }
    query = "userName eq \"" + userID +"\""
    payload = { 'filter' : query }
    res = requests.get(scimUserEndpoint, headers=headers, params=payload, verify=False)
    user = (res.json())['Resources']
    return user[0]['id']

def getUserAttributes( inum, scimUserEndpoint, token):
    headers = { 'content-type': "application/x-www-form-urlencoded", 'Authorization' : createBearerToken(token) }
    url = scimUserEndpoint + "/" + inum
    res = requests.get(url, headers=headers, verify=False)
    return res.json()

def addUserAttribute( inum, attributePath, newValue, scimUserEndpoint, token):
    #TODO finish implementation
    headers = { 'content-type': "application/x-www-form-urlencoded", 'Authorization' : createBearerToken(token) }
    operation = "{ \"op\":\"add\", \"path\": \"" + attributePath + "\", \"value\":\"" + newValue + "\"}"
    payload = "{ \"Operations\" : [" + operation + "]}"
    print(payload)
    res = requests.patch(scimUserEndpoint, data=payload, headers=headers, verify=False)
    print(res)
    return

def editUserAttribute( inum, attributePath, newValue, scimUserEndpoint, token):
    #TODO finish implementation
    headers = { 'content-type': "application/x-www-form-urlencoded", 'Authorization' : createBearerToken(token) }
    operation = "{ \"op\":\"replace\", \"path\": \"" + attributePath + "\", \"value\":\"" + newValue + "\"}"
    payload = "{ \"Operations\" : [" + operation + "]}"
    print(payload)
    res = requests.patch(scimUserEndpoint, data=payload, headers=headers, verify=False)
    print(res)
    return

def removeUserAttribute( inum, attributePath, scimUserEndpoint):
    #TODO finish implementation
    headers = { 'content-type': "application/x-www-form-urlencoded", 'Authorization' : createBearerToken(token) }
    operation = "{ \"op\":\"remove\", \"path\": \"" + attributePath + "\"}"
    payload = "{ \"Operations\" : [" + operation + "]}"
    print(payload)
    res = requests.patch(scimUserEndpoint, data=payload, headers=headers, verify=False)
    print(res)
    return

#a = registerClient("https://demoexample.gluu.org/oxauth/restv1/register", "TestClientGluu", ["https://demoexample.gluu.org/identity/authentication/getauthcode"])
#credentials = createCredentials(a['client_id'], a['client_secret'])
credentials = createCredentials('@!C28A.A0EC.7CA4.6154!0001!94C2.0974!0008!DF1E.BCB8.1E0E.91AE', 'secret')
token = getAccessToken("https://demoexample.gluu.org/oxauth/restv1/token", credentials, ["https://demoexample.gluu.org/identity/authentication/getauthcode"])
inum = getUserInum('tiago@test.com', 'https://demoexample.gluu.org/identity/restv1/scim/v2/Users', token)
print(getUserAttributes(inum, 'https://demoexample.gluu.org/identity/restv1/scim/v2/Users', token))
print(editUserAttribute(inum, "name.familyName", "M Fernandes", 'https://demoexample.gluu.org/identity/restv1/scim/v2/Users', token))
print(getUserAttributes(inum, 'https://demoexample.gluu.org/identity/restv1/scim/v2/Users', token))