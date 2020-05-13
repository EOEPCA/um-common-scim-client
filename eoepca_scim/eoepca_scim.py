import requests
import json
import sys
import base64
import time
import traceback
import urllib
import logging
import datetime
from jwkest.jws import JWS
from jwkest.jwk import RSAKey, import_rsa_key_from_file, load_jwks_from_url, import_rsa_key
from jwkest.jwk import load_jwks
from Crypto.PublicKey import RSA

class EOEPCA_Scim:
    __REGISTER_ENDPOINT = "/oxauth/restv1/register"
    __TOKEN_ENDPOINT = "/oxauth/restv1/token"
    __SCIM_USERS_ENDPOINT = "/identity/restv1/scim/v2/Users"
    __JWKS_ENDPOINT = "/oxauth/restv1/jwks"

    def __init__(self, host, clientID=None, clientSecret=None, jks_path=None, kid=None):
        self.client_id = clientID
        self.client_secret = clientSecret
        self.host = host
        self.jks_path = jks_path
        self._kid = kid if kid != None else "RSA1"
        self.access_token = None
        self.authRetries = 3
        self.usingUMA = 0 if self.jks_path == None else 1

    def __generateRSAKeyPair(self):
        _rsakey = RSA.generate(2048)
        self._private_key = _rsakey.exportKey()
        self._public_key = _rsakey.publickey().exportKey()

        file_out = open("private.pem", "wb")
        file_out.write(self._private_key)
        file_out.close()

        file_out = open("public.pem", "wb")
        file_out.write(self._public_key)
        file_out.close()

        return

    def __getRSAPrivateKey(self):
        return self._private_key

    def __getRSAPublicKey(self):
        return self._public_key

    def registerClient(self, clientName, grantTypes, redirectURIs, logoutURI, responseTypes, scopes, useUMA=0):
        logging.info("Registering new client...")
        headers = { 'content-type': "application/scim+json"}
        if useUMA == 1:
            self.__generateRSAKeyPair()
            self.usingUMA = 1
        payload = self.clientPayloadCreation(clientName, grantTypes, redirectURIs, logoutURI, responseTypes, scopes, useUMA)
        res = requests.post(self.host+self.__REGISTER_ENDPOINT, data=payload, headers=headers, verify=False)
        matrix = res.json()
        self.client_id = matrix['client_id']
        self.client_secret = matrix['client_secret']
        logging.info("New client " + clientName + " successfully created!")
        return matrix

    def __create_jwt(self):
        if self.jks_path != None:
            _rsajwk = RSAKey(kid=self._kid, key=import_rsa_key_from_file(self.jks_path))
        else:
            _rsajwk = RSAKey(kid=self._kid, key=import_rsa_key(self.__getRSAPrivateKey()))
        _payload = { 
                    "iss": self.client_id,
                    "sub": self.client_id,
                    "aud": self.host+self.__TOKEN_ENDPOINT,
                    "jti": datetime.datetime.today().strftime('%Y%m%d%s'),
                    "exp": int(time.time())+3600
                }
        _jws = JWS(_payload, alg="RS256")
        return _jws.sign_compact(keys=[_rsajwk])

    def __getUMAAccessToken(self, ticket, jwt):
        logging.info("UMA Token invalid, generating new one...")
        if self.client_id == None:
            logging.info("No client id found, please register first.")
            return None
        headers = { 'content-type': "application/x-www-form-urlencoded", 'cache-control': "no-cache" }
        payload = {'grant_type' : "urn:ietf:params:oauth:grant-type:uma-ticket", 'client_id' : self.client_id, 'client_assertion_type': "urn:ietf:params:oauth:client-assertion-type:jwt-bearer", 'ticket': ticket, 'client_assertion': jwt }
        msg = "Host unreachable"
        status = 404
        try:
            res = requests.post(self.host+self.__TOKEN_ENDPOINT, data=payload, headers=headers, verify=False)
            status = res.status_code
            if status == 200:
                self.access_token = res.json()["access_token"]
        except:
            logging.error(traceback.format_exc())
        return

    def __getOAuthAccessToken(self, credentials):
        logging.info("OAuth Token invalid, generating new one...")
        if credentials == None:
            logging.info("No client id or secret found, please register first.")
            return None
        headers = { 'content-type': "application/x-www-form-urlencoded", 'Authorization' : credentials }
        payload = {'grant_type' : 'client_credentials'}
        try:
            res = requests.post(self.host + self.__TOKEN_ENDPOINT, headers=headers, data=payload, verify=False)
            status = res.status_code
            if status == 200:
                self.access_token = res.json()["access_token"]
        except:
            logging.error(traceback.format_exc())
        return

    def createOAuthCredentials(self, client_id, client_secret):
        message = client_id + ':' + client_secret
        message_bytes = message.encode('utf-8')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('utf-8')
        credentials = 'Basic ' + base64_message
        return credentials

    def createBearerToken(self, token):
        return 'Bearer ' + token

    def __getUserInum(self, userID):
        logging.info("Fetching User INUM for user " + userID + "...")
        if self.access_token != None:
            headers = { 'content-type': "application/x-www-form-urlencoded", 'Authorization' : self.createBearerToken(self.access_token)}
        else:
            headers = { 'content-type': 'application/x-www-form-urlencoded', 'Authorization': self.createBearerToken('0')}
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
            logging.error(traceback.format_exc())
        if self.authRetries == 0:
            logging.error("Maximum number of attempts reached, re-register client.")
            return "0"
        if status == 401:
            if self.usingUMA == 1:
                self.__getUMAAccessToken(res.headers["WWW-Authenticate"].split("ticket=")[1], self.__create_jwt())
            else:
                self.__getOAuthAccessToken(self.createOAuthCredentials(self.client_id, self.client_secret))
            self.authRetries -= 1
            return self.__getUserInum(userID)
        elif status == 500:
            self.access_token = None
            return self.__getUserInum(userID)
        user = (res.json())['Resources']
        self.client_id = user[0]['id']
        logging.info("User INUM found!")
        self.authRetries = 3
        return user[0]['id']

    def getUserAttributes(self, userID):
        logging.info("Fetching user " + userID + " attributes...")
        if self.client_id == None:
            logging.info("No client id found, please register first.")
            return None
        url = self.host + self.__SCIM_USERS_ENDPOINT + "/" + self.__getUserInum(userID)
        if self.access_token != None:
            headers = { 'content-type': "application/x-www-form-urlencoded", 'Authorization' : self.createBearerToken(self.access_token)}
        else:
            headers = { 'content-type': 'application/x-www-form-urlencoded', 'Authorization': self.createBearerToken('0')}
        msg = "Host unreachable"
        status = 404
        try:
            res = requests.get(url, headers=headers, verify=False)
            status = res.status_code
            msg = res.text
        except:
            logging.error(traceback.format_exc())
        if self.authRetries == 0:
            logging.error("Maximum number of attempts reached, re-register client.")
            return "0"
        if status == 401:
            if self.usingUMA == 1:
                self.__getUMAAccessToken(res.headers["WWW-Authenticate"].split("ticket=")[1], self.__create_jwt())
            else:
                self.__getOAuthAccessToken(self.createOAuthCredentials(self.client_id, self.client_secret))
            self.authRetries -= 1
            return self.getUserAttributes(userID)
        elif status == 500:
            self.access_token = None
            return self.getUserAttributes(userID)
        logging.info("User attributes found, returning.")
        self.authRetries = 3
        return res.json()

    def addUserAttribute(self, userID, attributePath, newValue):
        logging.info("Adding attribute " + attributePath + ", with value " + newValue + " to user " + userID)
        if self.client_id == None:
            logging.info("No client id found, please register first.")
            return None
        url = self.host + self.__SCIM_USERS_ENDPOINT + "/" + self.__getUserInum(userID)
        if self.access_token != None:
            headers = { 'content-type': "application/scim+json", 'Authorization' : self.createBearerToken(self.access_token)}
        else:
            headers = { 'content-type': 'application/x-www-form-urlencoded', 'Authorization': self.createBearerToken('0')}
        operation = "{ \"op\":\"add\", \"path\": \"" + attributePath + "\", \"value\":\"" + newValue + "\"}"
        payload = "{ \"Operations\" : [" + operation + "]}"
        msg = "Host unreachable"
        status = 404
        try:
            res = requests.patch(url, data=payload, headers=headers, verify=False)
            status = res.status_code
            msg = res.text
        except:
            logging.error(traceback.format_exc())
        if self.authRetries == 0:
            logging.error("Maximum number of attempts reached, re-register client.")
            return "0"
        if status == 401:
            if self.usingUMA == 1:
                self.__getUMAAccessToken(res.headers["WWW-Authenticate"].split("ticket=")[1], self.__create_jwt())
            else:
                self.__getOAuthAccessToken(self.createOAuthCredentials(self.client_id, self.client_secret))
            self.authRetries -= 1
            return self.addUserAttribute(userID, attributePath, newValue)
        elif status == 500:
            self.access_token = None
            return self.addUserAttribute(userID, attributePath, newValue)
        logging.info("Attribute successfully added.")
        self.authRetries = 3
        return status

    def editUserAttribute(self, userID, attributePath, newValue):
        if self.client_id == None:
            logging.info("No client id found, please register first.")
            return None
        url = self.host + self.__SCIM_USERS_ENDPOINT + "/" + self.__getUserInum(userID)
        if self.access_token != None:
            headers = { 'content-type': "application/scim+json", 'Authorization' : self.createBearerToken(self.access_token)}
        else:
            headers = { 'content-type': 'application/x-www-form-urlencoded', 'Authorization': self.createBearerToken('0')}
        operation = "{ \"op\":\"replace\", \"path\": \"" + attributePath + "\", \"value\":\"" + newValue + "\"}"
        payload = "{ \"Operations\" : [" + operation + "]}"
        msg = "Host unreachable"
        status = 404
        try:
            res = requests.patch(url, data=payload, headers=headers, verify=False)
            status = res.status_code
            msg = res.text
        except:
            logging.error(traceback.format_exc())
        if self.authRetries == 0:
            logging.error("Maximum number of attempts reached, re-register client.")
            return 401
        if status == 401:
            if self.usingUMA == 1:
                self.__getUMAAccessToken(res.headers["WWW-Authenticate"].split("ticket=")[1], self.__create_jwt())
            else:
                self.__getOAuthAccessToken(self.createOAuthCredentials(self.client_id, self.client_secret))
            return self.editUserAttribute(userID, attributePath, newValue)
        elif status == 500:
            self.access_token = None
            return self.editUserAttribute(userID, attributePath, newValue)
        self.authRetries = 3
        return status

    def removeUserAttribute(self, userID, attributePath):
        if self.client_id == None:
            logging.info("No client id found, please register first.")
            return None
        url = self.host + self.__SCIM_USERS_ENDPOINT + "/" + self.__getUserInum(userID)
        if self.access_token != None:
            headers = { 'content-type': "application/scim+json", 'Authorization' : self.createBearerToken(self.access_token)}
        else:
            headers = { 'content-type': 'application/x-www-form-urlencoded', 'Authorization': self.createBearerToken('0')}
        operation = "{ \"op\":\"remove\", \"path\": \"" + attributePath + "\"}"
        payload = "{ \"Operations\" : [" + operation + "]}"
        msg = "Host unreachable"
        status = 404
        try:
            res = requests.patch(url, data=payload, headers=headers, verify=False)
            status = res.status_code
            msg = res.text
        except:
            logging.error(traceback.format_exc())
        if self.authRetries == 0:
            logging.error("Maximum number of attempts reached, re-register client.")
            return 401
        if status == 401:
            if self.usingUMA == 1:
                self.__getUMAAccessToken(res.headers["WWW-Authenticate"].split("ticket=")[1], self.__create_jwt())
            else:
                self.__getOAuthAccessToken(self.createOAuthCredentials(self.client_id, self.client_secret))
            self.authRetries -= 1
            return self.removeUserAttribute(userID, attributePath)
        elif status == 500:
            self.access_token = None
            return self.removeUserAttribute(userID, attributePath)
        self.authRetries = 3
        return status

    def deleteUser(self, userID):
        logging.info("Deleting user " + userID)
        if self.client_id == None:
            logging.info("No client id found, please register first.")
            return None
        url = self.host + self.__SCIM_USERS_ENDPOINT + "/" + self.__getUserInum(userID)
        if self.access_token != None:
            headers = { 'content-type': "application/x-www-form-urlencoded", 'Authorization' : self.createBearerToken(self.access_token)}
        else:
            headers = { 'content-type': 'application/x-www-form-urlencoded', 'Authorization': self.createBearerToken('0')}
        msg = "Host unreachable"
        status = 404
        try:
            res = requests.delete(url, headers=headers, verify=False)
            status = res.status_code
            msg = res.text
        except:
            logging.error(traceback.format_exc())
        if self.authRetries == 0:
            logging.error("Maximum number of attempts reached, re-register client.")
            return 0
        if status == 401:
            if self.usingUMA == 1:
                self.__getUMAAccessToken(res.headers["WWW-Authenticate"].split("ticket=")[1], self.__create_jwt())
            else:
                self.__getOAuthAccessToken(self.createOAuthCredentials(self.client_id, self.client_secret))
            self.authRetries -= 1
            return self.getUserAttributes(userID)
        elif status == 500:
            self.access_token = None
            return self.getUserAttributes(userID)
        logging.info("User deleted.")
        self.authRetries = 3
        return status

    def clientPayloadCreation(self, clientName, grantTypes, redirectURIs, logoutURI, responseTypes, scopes, useUMA=0):
        payload = "{ \"client_name\": \"" + clientName + "\", \"grant_types\":["
        for grant in grantTypes:
            payload += "\"" + grant.strip() + "\", "
        payload = payload[:-2] + "], \"redirect_uris\" : ["
        for uri in redirectURIs:
            payload += "\"" + uri.strip() + "\", "
        payload = payload[:-2] + "], \"post_logout_redirect_uris\": [\""+ logoutURI +"\"], \"scope\": \""
        for scope in scopes:
            payload += scope.strip() + " "
        payload = payload[:-1] + "\", \"response_types\": [  "
        for response in responseTypes:
            payload += "\"" + response.strip() + "\",  "
        payload = payload[:-2] + "]"
        if useUMA == 1:
            payload += ", \"jwks\": {\"keys\": [ " + str(RSAKey(kid=self._kid, key=import_rsa_key(self.__getRSAPublicKey()))) + "]}"
            payload += ", \"token_endpoint_auth_method\": \"private_key_jwt\""
        payload += "}"
        return payload
