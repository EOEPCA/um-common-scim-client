#!/usr/bin/env python3
from eoepca_scim import EOEPCA_Scim, ENDPOINT_AUTH_CLIENT_POST, ENDPOINT_AUTH_CLIENT_PRIVATE_KEY_JWT
import logging
# *** Use this for auto-contained examples ***

def main():
    logging.getLogger().setLevel(logging.INFO)

    #Determine Gluu host address
    gluuHost = "https://demoexample.gluu.org"

    #Initiate class
    scim_client = EOEPCA_Scim(host=gluuHost)

    #Initiate class with an existing user (INUM), specifying the location of their private RSA key file and kid (key ID) for UMA purposes
    #When no kid is provided, default value "RSA1" is used
    #scim_client = EOEPCA_Scim(host=gluuHost, clientID="", clientSecret="", jks_path="", kid="")

    #Register a new client, returns client information in JSON format
    clientName="TestClient"
    grantTypes=["client_credentials", "urn:ietf:params:oauth:grant-type:uma-ticket", "password", "implicit"]
    redirectURIs=["https://demoexample.gluu.org/web_ui/oauth/callback"]
    logoutURI="https://demoexample.gluu.org/logout"
    responseTypes=[]
    #Sector identifier is OPTIONAL field
    #Redirect URIs MUST be contained in Sector Identifier, if this is used
    sectorIdentifier="https://demoexample.gluu.org/oxauth/sectoridentifier/9b473868-fa96-4fd1-a662-76e3663c9726"
    #sectorIdentifiers=None
    #OpenID scope examples
    scopes=["openid", "oxd", "permission"]
    #UMA scope example
    #scopes=["https://demoexample.gluu.org/oxauth/restv1/uma/scopes/scim_access"]
    #Register call, with useJWK=1 if JWK is being used
    #clientJSON = scim_client.registerClient(clientName=clientName, grantTypes=grantTypes, redirectURIs=redirectURIs, logoutURI=logoutURI, responseTypes=responseTypes, scopes=scopes, token_endpoint_auth_method= ENDPOINT_AUTH_CLIENT_POST)
    clientJSON = scim_client.registerClient(clientName=clientName, grantTypes=grantTypes, redirectURIs=redirectURIs, logoutURI=logoutURI, responseTypes=responseTypes, scopes=scopes, sectorIdentifier=sectorIdentifier, token_endpoint_auth_method= ENDPOINT_AUTH_CLIENT_POST)
    #clientJSON = scim_client.registerClient(clientName=clientName, grantTypes=grantTypes, redirectURIs=redirectURIs, logoutURI=logoutURI, responseTypes=responseTypes, scopes=scopes, token_endpoint_auth_method= ENDPOINT_AUTH_CLIENT_PRIVATE_KEY_JWT , useJWK=1)
    print(clientJSON)

    #User to which we want to obtain all attributes
    userID = "test@test.com"

    #Get user attributes
    attributes = scim_client.getUserAttributes(userID=userID)
    print(attributes)

    #Add a new attribute
    attributePath="name.middleName"
    newValue="Middle"
    scim_client.addUserAttribute(userID=userID, attributePath=attributePath, newValue=newValue)
    
    #Modify an attribute
    attributePath="name.familyName"
    newValue="Last"
    scim_client.editUserAttribute(userID=userID, attributePath=attributePath, newValue=newValue)

    #Remove an attribute
    attributePath="name.middleName"
    scim_client.removeUserAttribute(userID=userID, attributePath=attributePath)
    
    #Delete user
    reply = scim_client.deleteUser(userID=userID)
    print(reply)

if __name__ == "__main__":
     
    main()
