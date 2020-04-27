import requests
import json
import sys
import base64
import time
import traceback
import urllib

class EOEPCA_Scim():
    __REGISTER_ENDPOINT = "/oxauth/restv1/register"
    __TOKEN_ENDPOINT = "/oxauth/restv1/token"
    __SCIM_USERS_ENDPOINT = "/identity/restv1/scim/v2/Users"

    def __init__(self, host):
        self.client_id = None
        self.host = host
        self.access_token = None

    def registerClient(self, clientName, redirectURIs, logoutURI, scopes):
        print("Registering new client...")
        headers = { 'content-type': "application/scim+json"}
        payload = "{ \"client_name\": \"" + clientName + "\", \"grant_types\":[\"client_credentials\", \"urn:ietf:params:oauth:grant-type:uma-ticket\"], \"redirect_uris\" : ["
        for uri in redirectURIs:
            payload += "\"" + uri.strip() + "\", "
        payload = payload[:-2] + "], \"post_logout_redirect_uris\": [\""+ logoutURI +"\"], \"scope\": "
        for scope in scopes:
            payload += "\"" + scope.strip() + "\" "
        payload = payload[:-1] + "}"
        res = requests.post(self.host+self.__REGISTER_ENDPOINT, data=payload, headers=headers, verify=False)
        matrix = res.json()
        self.client_id = matrix['client_id']
        self.client_secret = matrix['client_secret']
        print("New client " + clientName + " successfully created!")
        return matrix

    def __getOAuthAccessToken(self, credentials):
        print("OAuth Token invalid, generating new one...")
        if credentials == None:
            print("No client id or secret found, please register first.")
            return None
        headers = { 'content-type': "application/x-www-form-urlencoded", 'Authorization' : credentials }
        payload = {'grant_type' : 'client_credentials'}
        try:
            res = requests.post(self.host + self.__TOKEN_ENDPOINT, headers=headers, data=payload, verify=False)
            status = res.status_code
            self.access_token = res.json()["access_token"]
        except:
            print(traceback.format_exc())
        return

    def __createOAuthCredentials(self, client_id, client_secret):
        message = client_id + ':' + client_secret
        message_bytes = message.encode('utf-8')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('utf-8')
        credentials = 'Basic ' + base64_message
        return credentials

    def __createBearerToken(self, token):
        return 'Bearer ' + token

    def __getUserInum(self, userID):
        print("Fetching User INUM for user " + userID + "...")
        if self.access_token != None:
            headers = { 'content-type': "application/x-www-form-urlencoded", 'Authorization' : self.__createBearerToken(self.access_token)}
        else:
            headers = { 'content-type': 'application/x-www-form-urlencoded', 'Authorization': self.__createBearerToken('0')}
        msg = "Host unreachable"
        status = 404
        query = "userName eq \"" + userID +"\""
        payload = { 'filter' : query }
        url = self.host+self.__SCIM_USERS_ENDPOINT
        try:
            res = requests.get(url, headers=headers, params=payload, verify=False)
            status = res.status_code
            msg = res.text
        except:
            print(traceback.format_exc())
        if status == 401:
            self.__getOAuthAccessToken(self.__createOAuthCredentials(self.client_id, self.client_secret))
            return self.__getUserInum(userID)
        elif status == 500:
            self.access_token = None
            return self.__getUserInum(userID)
        user = (res.json())['Resources']
        self.client_id = user[0]['id']
        print("User INUM found!")
        return user[0]['id']

    def getUserAttributes(self, userID):
        print("Fetching user " + userID + " attributes...")
        if self.client_id == None:
            print("No client id found, please register first.")
            return None
        url = self.host + self.__SCIM_USERS_ENDPOINT + "/" + self.__getUserInum(userID)
        if self.access_token != None:
            headers = { 'content-type': "application/x-www-form-urlencoded", 'Authorization' : self.__createBearerToken(self.access_token)}
        else:
            headers = { 'content-type': 'application/x-www-form-urlencoded', 'Authorization': self.__createBearerToken('0')}
        msg = "Host unreachable"
        status = 404
        try:
            res = requests.get(url, headers=headers, verify=False)
            status = res.status_code
            msg = res.text
            print(status)
            print(msg)
        except:
            print(traceback.format_exc())
        if status == 401:
            self.__getOAuthAccessToken(self.__createOAuthCredentials(self.client_id, self.client_secret))
            return self.getUserAttributes(userID)
        elif status == 500:
            self.access_token = None
            return self.getUserAttributes(userID)
        print("User attributes found, returning.")
        return res.json()

    def addUserAttribute(self, userID, attributePath, newValue):
        print("Adding attribute " + attributePath + ", with value " + newValue + " to user " + userID)
        if self.client_id == None:
            print("No client id found, please register first.")
            return None
        url = self.host + self.__SCIM_USERS_ENDPOINT + "/" + self.__getUserInum(userID)
        if self.access_token != None:
            headers = { 'content-type': "application/x-www-form-urlencoded", 'Authorization' : self.__createBearerToken(self.access_token)}
        else:
            headers = { 'content-type': 'application/x-www-form-urlencoded', 'Authorization': self.__createBearerToken('0')}
        operation = "{ \"op\":\"add\", \"path\": \"" + attributePath + "\", \"value\":\"" + newValue + "\"}"
        payload = "{ \"Operations\" : [" + operation + "]}"
        msg = "Host unreachable"
        status = 404
        try:
            res = requests.patch(url, data=payload, headers=headers, verify=False)
            status = res.status_code
            msg = res.text
        except:
            print(traceback.format_exc())
        if status == 401:
            self.__getOAuthAccessToken(self.__createOAuthCredentials(self.client_id, self.client_secret))
            return self.addUserAttribute(userID, attributePath, newValue)
        elif status == 500:
            self.access_token = None
            return self.addUserAttribute(userID, attributePath, newValue)
        print("Attribute successfully added.")
        return status

    def editUserAttribute(self, userID, attributePath, newValue):
        if self.client_id == None:
            print("No client id found, please register first.")
            return None
        url = self.host + self.__SCIM_USERS_ENDPOINT + "/" + self.__getUserInum(userID)
        if self.access_token != None:
            headers = { 'content-type': "application/x-www-form-urlencoded", 'Authorization' : self.__createBearerToken(self.access_token)}
        else:
            headers = { 'content-type': 'application/x-www-form-urlencoded', 'Authorization': self.__createBearerToken('0')}
        operation = "{ \"op\":\"replace\", \"path\": \"" + attributePath + "\", \"value\":\"" + newValue + "\"}"
        payload = "{ \"Operations\" : [" + operation + "]}"
        msg = "Host unreachable"
        status = 404
        try:
            res = requests.patch(url, data=payload, headers=headers, verify=False)
            status = res.status_code
            msg = res.text
        except:
            print(traceback.format_exc())
        if status == 401:
            self.__getOAuthAccessToken(self.__createOAuthCredentials(self.client_id, self.client_secret))
            return self.editUserAttribute(userID, attributePath, newValue)
        elif status == 500:
            self.access_token = None
            return self.editUserAttribute(userID, attributePath, newValue)
        return status

    def removeUserAttribute(self, userID, attributePath, newValue):
        if self.client_id == None:
            print("No client id found, please register first.")
            return None
        url = self.host + self.__SCIM_USERS_ENDPOINT + "/" + self.__getUserInum(userID)
        if self.access_token != None:
            headers = { 'content-type': "application/x-www-form-urlencoded", 'Authorization' : self.__createBearerToken(self.access_token)}
        else:
            headers = { 'content-type': 'application/x-www-form-urlencoded', 'Authorization': self.__createBearerToken('0')}
        operation = "{ \"op\":\"remove\", \"path\": \"" + attributePath + "\"}"
        payload = "{ \"Operations\" : [" + operation + "]}"
        msg = "Host unreachable"
        status = 404
        try:
            res = requests.patch(url, data=payload, headers=headers, verify=False)
            status = res.status_code
            msg = res.text
        except:
            print(traceback.format_exc())
        if status == 401:
            self.__getOAuthAccessToken(self.__createOAuthCredentials(self.client_id, self.client_secret))
            return self.removeUserAttribute(userID, attributePath, newValue)
        elif status == 500:
            self.access_token = None
            return self.removeUserAttribute(userID, attributePath, newValue)
        return status
