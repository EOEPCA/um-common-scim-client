#!/usr/bin/env python3
import json
from eoepca_scim import EOEPCA_Scim

def initEOEPCAScim():
    #placeholder domain
    gluuHost = "https://demoexample.gluu.org"

    #Initiate class
    return EOEPCA_Scim(host=gluuHost)

def testInit():
    eoepca_scim = initEOEPCAScim()
    assert eoepca_scim != None

def testCreateBearerToken():
    eoepca_scim = initEOEPCAScim()
    token = "AbCd1234#"
    expectedAnswer = "Bearer " + token
    returnedToken = eoepca_scim.createBearerToken(token)
    assert returnedToken == expectedAnswer

def testCreateOAuthCredentials():
    eoepca_scim = initEOEPCAScim()
    clientID = "TestID"
    clientSecret = "TestSecret"
    expectedAnswer = "Basic VGVzdElEOlRlc3RTZWNyZXQ="
    answer = eoepca_scim.createOAuthCredentials(clientID, clientSecret)
    assert answer == expectedAnswer

def testClientPayloadCreation():
    eoepca_scim = initEOEPCAScim()
    clientName="TestClient"
    grantTypes=["client_credentials", "urn:ietf:params:oauth:grant-type:uma-ticket"]
    redirectURIs=["https://demoexample.gluu.org/login"]
    logoutURI="https://demoexample.gluu.org/logout"
    responseTypes=[]
    scopes=["openid", "oxd", "permission"]
    expectedAnswer="{ \"client_name\": \"TestClient2\", \"grant_types\":[\"client_credentials\", \"urn:ietf:params:oauth:grant-type:uma-ticket\"], \"redirect_uris\" : [\"https://demoexample.gluu.org/login\"], \"post_logout_redirect_uris\": [\"https://demoexample.gluu.org/logout\"], \"scope\": \"openid oxd permission\", \"response_types\": []}"
    payloadJSON = eoepca_scim.clientPayloadCreation(clientName=clientName, grantTypes=grantTypes, redirectURIs=redirectURIs, logoutURI=logoutURI, responseTypes=responseTypes, scopes=scopes)
    payloadString = json.dumps(payloadJSON)
    assert payloadString == expectedAnswer
