import requests
import json
import sys
import base64

def registerClient( targetURL, clientName, redirectURIs):
    headers = { 'content-type': "application/scim+json"}
    payload = "{ \"client_name\": \"" + clientName + "\", \"grant_types\":[\"client_credentials\"], \"redirect_uris\" : ["
    for uri in redirectURIs:
        payload += "\"" + uri.strip() + "\", "
    payload = payload[:-2]
    payload += "]}"
    res = requests.post(targetURL, data=payload, headers=headers, verify=False)
    matrix = res.json()
    return (matrix)

def getAccessToken( token_endpoint, credentials, redirectURIs):
    headers = { 'content-type': "application/x-www-form-urlencoded", 'Authorization' : credentials }
    payload = {'grant_type' : 'client_credentials'}

    res = requests.post(token_endpoint, headers=headers, data=payload, verify=False)
    matrix = res.json()
    return matrix['access_token']

def createCredentials( client_id, client_secret):
    message = client_id + ':' + client_secret
    message_bytes = message.encode('utf-8')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('utf-8')
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
    url = scimUserEndpoint + "/" + inum
    headers = { 'content-type': "application/scim+json", 'Authorization' : createBearerToken(token) }
    operation = "{ \"op\":\"add\", \"path\": \"" + attributePath + "\", \"value\":\"" + newValue + "\"}"
    payload = "{ \"Operations\" : [" + operation + "]}"
    res = requests.patch(url, data=payload, headers=headers, verify=False)
    return res.json()

def editUserAttribute( inum, attributePath, newValue, scimUserEndpoint, token):
    url = scimUserEndpoint + "/" + inum
    headers = { 'content-type': "application/scim+json", 'Authorization' : createBearerToken(token) }
    operation = "{ \"op\":\"replace\", \"path\": \"" + attributePath + "\", \"value\":\"" + newValue + "\"}"
    payload = "{ \"Operations\" : [" + operation + "]}"
    res = requests.patch(url, data=payload, headers=headers, verify=False)
    return res.json()

def removeUserAttribute( inum, attributePath, scimUserEndpoint, token):
    url = scimUserEndpoint + "/" + inum
    headers = { 'content-type': "application/scim+json", 'Authorization' : createBearerToken(token) }
    operation = "{ \"op\":\"remove\", \"path\": \"" + attributePath + "\"}"
    payload = "{ \"Operations\" : [" + operation + "]}"
    res = requests.patch(url, data=payload, headers=headers, verify=False)
    return res.json()

#a = registerClient("https://demoexample.gluu.org/oxauth/restv1/register", "TestClientGluu", ["https://demoexample.gluu.org/identity/authentication/getauthcode"])
#credentials = createCredentials(a['client_id'], a['client_secret'])
#credentials = createCredentials('@!C28A.A0EC.7CA4.6154!0001!94C2.0974!0008!DF1E.BCB8.1E0E.91AE', 'secret')
#token = getAccessToken("https://demoexample.gluu.org/oxauth/restv1/token", credentials, ["https://demoexample.gluu.org/identity/authentication/getauthcode"])
#inum = getUserInum('tiago@test.com', 'https://demoexample.gluu.org/identity/restv1/scim/v2/Users', token)
#print(getUserAttributes(inum, 'https://demoexample.gluu.org/identity/restv1/scim/v2/Users', token))
#print(editUserAttribute(inum, "name.familyName", "M Fernandes", 'https://demoexample.gluu.org/identity/restv1/scim/v2/Users', token))
#print(addUserAttribute(inum, "name.middleName", "M", 'https://demoexample.gluu.org/identity/restv1/scim/v2/Users', token))
#print(removeUserAttribute(inum, "name.middleName", 'https://demoexample.gluu.org/identity/restv1/scim/v2/Users', token))
#print(getUserAttributes(inum, 'https://demoexample.gluu.org/identity/restv1/scim/v2/Users', token))