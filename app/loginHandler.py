import json
from json import JSONDecoder, JSONEncoder

class LoginHandler:
    # Handles login process, compares username and password provided
    credentialFile = "credentials.json"

    # Instance fields include request, response, logFlag, and logFile

    def __init__(self,request,response):
        # Set Http request and response objects
        self.request = request
        self.response = response
        # Set logFlag to true if you want a log file
        self.logFlag = False
        if(self.logFlag):
            self.logFile = open("logFile.dat","w")

        response.headers.add("Content-Type","application/json")

    def login(self):
        try:
            self.response.headers["Content-Type"] = "application/json"
            if(self.logFlag):
                self.logFile.write(str(self.request))
                self.logFile.write(self.request.headers['Content-Type'])
            assert(self.request.headers['Content-Type'] == "application/json"),"Must pass in json"
            # Get the JSON out of the request
            loginDict = self.request.get_json()
            #print(type(loginJson))
            #print(loginJson)
            # Convert the JSON to a dictionary
            #print('{"foo":"bar"}')

            #loginDict = self.decoder.decode(loginJson,encoding)#json.loads('{"foo":"bar"}') #loginJson)
            if(self.logFlag):
                self.logFile.write(str(loginDict)+"\n")
            assert(isinstance(loginDict,dict)),"Failed to create a dictionary out of json"
            # Make sure username and password are present
            if(not('username' in loginDict)):
                raise KeyError("Missing username")
            elif(not('password' in loginDict)):
                raise KeyError("Missing password")
            username = loginDict['username']
            if(self.logFlag):
                self.logFile.write("Loaded username"+"\n")
            password = loginDict['password']
            if(self.logFlag):
                self.logFile.write("Loaded password"+"\n")
            # For now import credentials list from a JSON file
            credJson = open(self.credentialFile,"r").read()
            if(self.logFlag):
                self.logFile.write(credJson+"\n")
                self.logFile.write(str(type(credJson))+"\n")

            credDict = json.loads(credJson)
            if(self.logFlag):
                self.logFile.write(str(type(credDict))+"\n")
                self.logFile.write(str(credDict)+"\n")
                self.logFile.write("Checking for:"+"\n")
                self.logFile.write(username+"\n")
                self.logFile.write(password+"\n")
                self.logFile.write("Checking username and password"+"\n")

            # Check for valid username and password
            if(not(username in credDict)):
                if(self.logFlag):
                    self.logFile.write("Bad username"+"\n")
                raise ValueError("Not a recognized user")
            elif(credDict[username] != password):
                if(self.logFlag):
                    self.logFile.write("Bad password"+"\n")
                raise ValueError("Incorrect password")
            else:
                # We have a valid login
                if(self.logFlag):
                    self.logFile.write("Valid login"+"\n")
                self.response.status_code = 200
                self.response.set_data(json.dumps({"message":"Login successful"}))
                return self.response


        except AssertionError as e:
            # Return a 400 with appropriate message
            if(self.logFlag):
                self.logFile.write("AssertionError"+"\n")
            self.response.status_code = 400
            self.response.set_data(json.dumps({"message":(e.message+","+str(self.request.get_json))}))
        except KeyError as e:
            # Return a 400 passing message forward
            if(self.logFlag):
                self.logFile.write("KeyError"+"\n")
            self.response.status_code = 400
            self.response.set_data(json.dumps({"message":e.message}))
        except ValueError as e:
            # Return a 400 passing message forward
            if(self.logFlag):
                self.logFile.write("ValueError"+"\n")
            self.response.status_code = 400
            self.response.set_data(json.dumps({"message":e.message}))
        return self.response