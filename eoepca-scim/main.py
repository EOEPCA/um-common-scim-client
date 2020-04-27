#!/usr/bin/env python3

# *** Use this for auto-contained examples ***

def main():
    #Determine Gluu host address
    gluuHost = "https://demoexample.gluu.org"

    #Initiate class
    scim_client = EOEPCA_Scim(host=gluuHost)

    #Register a new client, returns client information in JSON format
    clientJSON = scim_client.registerClient(clientName="TestClient1", redirectURIs=["https://demoexample.gluu.org/login"], logoutURI="https://demoexample.gluu.org/logout", scopes=["openid oxd permission"])
    print(clientJSON)

    #User to which we want to obtain all attributes
    userID = "tiago@test.com"

    #Get user attributes
    attributes = scim_client.getUserAttributes(userID=userID)
    print(attributes)

if __name__ == "__main__":
     
    main()