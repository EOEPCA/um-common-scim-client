#!/usr/bin/env python3
from eoepca_scim import EOEPCA_Scim
# *** Use this for auto-contained examples ***

def main():
#    importlib.import_module('eoepca_scim')
    #Determine Gluu host address
    gluuHost = "https://demoexample.gluu.org"

    #Initiate class
    scim_client = EOEPCA_Scim(host=gluuHost)

    #Register a new client, returns client information in JSON format
    clientName="TestClient"
    grantTypes=["client_credentials", "urn:ietf:params:oauth:grant-type:uma-ticket"]
    redirectURIs=["https://demoexample.gluu.org/login"]
    logoutURI="https://demoexample.gluu.org/logout"
    responseTypes=[]
    scopes=["openid", "oxd", "permission"]
    clientJSON = scim_client.registerClient(clientName=clientName, grantTypes=grantTypes, redirectURIs=redirectURIs, logoutURI=logoutURI, responseTypes=responseTypes, scopes=scopes)
    print(clientJSON)

    # #User to which we want to obtain all attributes
    userID = "test@test.com"

    # #Get user attributes
    attributes = scim_client.getUserAttributes(userID=userID)
    print(attributes)

if __name__ == "__main__":
     
    main()