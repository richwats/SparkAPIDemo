## Spark Class Object ##
import requests
# from oauthlib.oauth2 import WebApplicationClient
# from requests_oauthlib import OAuth2Session
from furl import furl
from collections import OrderedDict
import json
import urllib
import configparser
import os


class SparkMessage(object):
    ## Spark Message Object ##
    text = None
    markdown = None
    files = None
    roomId = None
    
    def __init__(self, text = None, markdown = None, files = None, roomId = None):
        self.text = text
        self.markdown = markdown
        self.files = files
        self.roomId = roomId
        return

    def buildPayload(self):
        if self.roomId is None:
            raise Exception('No Room/Space ID Defined')
        
        payload = OrderedDict(roomId = self.roomId)
        
        if self.markdown is not None:
            payload['markdown'] = self.markdown
            
        if self.text is not None and self.markdown is None:
            ## Don't send Text if Markdown Defined ##
            payload['text'] = self.text
        
        if self.files is not None:
            payload['files'] = self.files
            
        return payload

class SparkAPI(object):
    ## Variables ##
    config = None
    authCode = None
    authClient = None
    accessToken = None
    logger = None
    serverURL = None
    session = None
    response = None
    
    verifySSL = True
    
    teamId = None
    teamName = None
    
    webhookName = None

    _client_id = None 
    _client_secret = None 
    
    _redirectURI = None
    _webhookTargetURL = None
    
    sparkVersion = None
    _sparkUrl = None
    sparkBaseURL = "%s%s/ " % (str(_sparkUrl),str(sparkVersion))
        
    ## Functions ##
    def __init__(self, logger):
        ## Set Logger ##
        self.logger = logger
        self.logger.info('[SparkAPI] Initialising SparkAPI Object')
        
        ## Load Environmental Variables ##
        try:
            self.webhookName = os.environ.get('WEBHOOK_NAME')
            self._client_id = os.environ.get('SPARK_INT_ID')
            self._client_id = os.environ.get('SPARK_INT_ID')
            self._client_secret = os.environ.get('SPARK_INT_SECRET')
            self._redirectURI = os.environ.get('SPARK_INT_REDIRECT_URI')
            self._webhookTargetURL = os.environ.get('WEBHOOK_URL')
            self.sparkVersion = os.environ.get('SPARK_API_VERSION')
            self._sparkUrl = os.environ.get('SPARK_API_URL')
        except Exception as e:
            self.logger.error('[SparkAPI] Initialisation Error: %s' % str(e))
            return
        
        """
        ENV WEBHOOK_NAME=SparkChatDemo-Messages
        ENV WEBHOOK_URL=
        ENV SPARK_API_VERSION=V1
        ENV SPARK_API_URL=https://api.ciscospark.com
        ENV SPARK_INT_ID=
        ENV SPARK_INT_SECRET=
        ENV SPARK_INT_REDIRECT_URI=
        """
        
        ## Load Config ##
        self.config = configparser.ConfigParser()
        self.config.read('/tmp/config.ini')
        
        if self.config:
            if 'AUTH CODE' in self.config.keys():
                self.authCode = self.config['AUTH CODE']['authCode']
                self.logger.debug('[SparkAPI] Setting Auth Code: %s' % str(self.authCode))
            if 'ACCESS TOKEN' in self.config.keys():
                self.accessToken = self.config['ACCESS TOKEN']['access_token']
                self.logger.debug('[SparkAPI] Setting Access Token: %s' % str(self.accessToken))
            if 'TEAM' in self.config.keys():
                self.teamName = self.config['TEAM']['teamName']
                self.teamId = self.config['TEAM']['teamId']
                self.logger.debug('[SparkAPI] Setting Team Name: %s' % str(self.teamName))


        ## Setup URL ##
        self._setupURL()
        
        ## Setup Session ##
        self._setupSession()
        
        ## Get Access Token ##
        #self._getAccessToken()
        
        ## Setup Session ##
        #self._setupSession()

        return
        
    
    def _setupURL(self):
        self.serverURL = furl(self.sparkBaseURL)
        self.serverURL.path = self.sparkVersion
        self.logger.info('[SparkAPI] Base Spark URL: %s' % str(self.serverURL))
        return 
    
    def _setupSession(self):
        ## Setup Requests Session ##
        self.session = requests.Session()
        
        ## Request Headers ##
        self.session.headers.update({'Content-type': 'application/json; charset=utf-8'})
        
        if self.accessToken:
            self.session.headers.update({'Authorization': 'Bearer %s' % str(self.accessToken)})
        
        #self.session.auth = HTTPBasicAuth(self.username, self.password)
        self.session.verify = self.verifySSL
        return 
    
    def setAccessToken(self, authCode):
        #self.authClient = WebApplicationClient(self._client_id)
        
        queryURL = self.serverURL
        queryURL.path.segments.append('access_token')
        self.logger.debug('[SparkAPI] Auth Token URL: %s' % str(queryURL))
        
        headers = {'Content-Type':'application/x-www-form-urlencoded'}
        data = {'grant_type':'authorization_code',
                'redirect_uri': self._redirectURI,
                'code': authCode,
                'client_id': self._client_id,
                'client_secret': self._client_secret
                }
        
        r = requests.post(queryURL, data=data, headers=headers)
        r.raise_for_status()
        self.logger.debug('[SparkAPI] Response Status: %s' % str(r.status_code))
        self.logger.debug('[SparkAPI] Auth Token Response: %s' % str(r.text))
        
        ## Force Ordered Dict ##
        jsonObj = json.loads(r.text,object_pairs_hook=OrderedDict)
        
        return jsonObj
            
    def queryURL(self, url = None, method = "GET", payload = None, path = None, args = None):
        ## Build Resource List ##
        # try:
        if url is None and path is not None:
            ## Build URL ##
            queryURL = self.serverURL
            
            if isinstance(path, list):
                ## Path is List ##
                queryURL.path = self.sparkVersion
                queryURL.path.segments.extend(path)
            else:
                ## Assume Path is String ##
                queryURL.path = self.sparkVersion
                queryURL.path.segments.append(path)
            
            if args is not None:
                ## Set Arguments ##
                queryURL.args.update(args)
        
        else:
            ## Use fully defined URL ##
            queryURL = furl(url)
                                
        self.logger.debug('[SparkAPI] Query URL: %s' % str(queryURL))
        
        method = str(method).upper()
        self.logger.debug('[SparkAPI] Query Method: %s' % str(method))
        
        
        if str(method) == "GET":
            self.response =  self.session.get(queryURL)
        
        elif str(method) == "DELETE":
            self.response =  self.session.delete(queryURL)
            
        elif str(method) == "POST":
            self.response =  self.session.post(queryURL,json = payload)
        
        elif str(method) == "PUT":
            self.response =  self.session.put(queryURL, json = payload)
        
        self.logger.debug('[SparkAPI] Request Headers : %s' % str(self.response.request.headers))
        
        ## Raise Exceptions ##            
        self.response.raise_for_status()
        self.logger.debug('[SparkAPI] Response Status: %s' % str(self.response.status_code))
        
        ## Force Ordered Dict ##
        jsonObj = json.loads(self.response.text,object_pairs_hook=OrderedDict)
        self.logger.debug('[SparkAPI] JSON Key List: %s' % str(list(jsonObj.keys())))           
        
        return {'status_code': self.response.status_code,
                'json': jsonObj,
                #'text': self.response.text
                }
        
        # except Exception as e:
        #     self.logger.error('[SparkAPI] Error: %s' % str(e))
        #     if self.response:
        #         status_code = self.response.status_code
        #     else:
        #         status_code = None
        #         
        #     return {'status_code': status_code,
        #             'message': str(e)
        #             }
    
   
    ### TEAMS ###
    
    def listTeams(self):
        ## List Available Teams ##
        self.logger.info('[SparkAPI.listTeams] List Available Teams')
        
        ## Query Spark API ##
        teamList = self.queryURL(method="GET", path="teams")
        self.logger.debug('[SparkAPI.listTeams] Query URL: %s' % str(self.queryURL))
        self.logger.debug('[SparkAPI.listTeams] Team List: %s' % str(teamList))
        
        return teamList
    
    
    def createTeam(self, teamName):
        ## Create New Team ##
        self.logger.info('[SparkAPI.createTeam] Create New Team')
        
        ## Query Spark API ##
        payload = {'name': str(teamName) }
        
        response = self.queryURL(method="POST", path="teams", payload = payload)
        self.logger.debug('[SparkAPI.createTeam] Query URL: %s' % str(self.queryURL))
        self.logger.debug('[SparkAPI.createTeam] Response: %s' % str(response))
        
        return response
    
    def selectTeam(self, teamId, teamName):
        ## Create New Team ##
        self.logger.info('[SparkAPI.selectTeam] Selecting Team: %s' % str(teamName))
        
        if self.config:
            self.config['TEAM'] = {'teamName': teamName,
                                   'teamId': teamId }

            with open('/tmp/config.ini', 'w') as configfile:
                self.config.write(configfile)
                configfile.close()
    
        return {'json': {'teamName': teamName }}
    
    
    ### ROOMS/SPACES ###
    
    
    
    def buildSpaceName(self, email):
        ## Build Space Name from Email ##
        return "Customer: %s" % str(email)
    
    def getSpaceByName(self, spaceName):
        ## Find or Create Space in Selected Team ##
        self.logger.info('[SparkAPI.getSpace] Space Name: %s' % str(spaceName))
        if self.teamId is None:
            self.logger.error('[SparkAPI.getSpace] No Team Selected')
            raise Exception('No Team Selected')
        
        ## Look for Space/Room ##
        payload = {
            'teamId': self.teamId
        }
        
        response = self.queryURL(method="GET", path="rooms", payload = payload)
        
        spaces = response['json']['items']
        for space in spaces:
            if space['title'] == str(spaceName):
                ## Matching Space Found ##
                self.logger.info('[SparkAPI.getSpace] Existing Space Found: %s' % str(space['title']))
                return space  ## item
        
        ## Create Space ##
        payload = {
            'teamId': self.teamId,
            'title': str(spaceName)
        }
        self.logger.info('[SparkAPI.getSpace] Creating New Space: %s' % str(spaceName))
        response = self.queryURL(method="POST", path="rooms", payload = payload)
        return response
    
    ### WEBHOOKS ###
    
    def buildWebhookName(self, email):
        ## Build Webhook Name from Email ##
        return "SparkChatWebhook-%s" % str(email)
    
    def registerWebhook(self, spaceId, email):
        ### Checks if Webhook exists for Space/Room and Registers if not present ###
        self.logger.info('[SparkAPI.registerWebhook] Registering Webhook for Space/RoomId: %s' % str(spaceId))
        
        ## Build Webhook Name ##
        webhookName = self.buildWebhookName(email)
        
        response = self.queryURL(method="GET", path="webhooks")
        webhooks = response['json']['items']
        
        for webhook in webhooks:
            # filters = str(webhook['filter']).split(",")
            # roomId = None
            # for entry in filters:
            #     tmpList = str(entry).split("=", maxsplit=1)
            #     if str(tmpList[0]) == "roomId":
            #         roomId = str(tmpList[1])
                
            if webhook['name'] == str(webhookName):
                ## Matching Webhook Found ##
                self.logger.info('[SparkAPI.registerWebhook] Existing Webhook Found: %s' % str(webhook['id']))
                return webhook  ## item
        
        self.logger.info('[SparkAPI.registerWebhook] Creating New Webhook: %s' % str(webhookName))
        
        payload = {
            'name': webhookName,
            'targetUrl': self._webhookTargetURL,
            'resource': 'messages',
            'event': 'all',
            #'filter': "roomId=%s" % str(spaceId),
            #'secret':  None
        }
        
        self.logger.debug('[SparkAPI.registerWebhook] Payload: %s' % str(payload))
        
        response = self.queryURL(method="POST", path="webhooks", payload = payload)
        self.logger.debug('[SparkAPI.registerWebhook] Response: %s' % str(response))
        return response
    
    ### MESSAGES ###
    
    def getMessageById(self, msgId):
        self.logger.info('[SparkAPI.getMessageById] Getting Message Id: %s' % str(msgId))
        
        response = self.queryURL(method="GET", path=['messages',str(msgId)])
        self.logger.debug('[SparkAPI.getMessageById] Response: %s' % str(response))
        return response
    
    def sendMessage(self, msgObj):
        ## Send Message to Space/Room ##
        payload = msgObj.buildPayload()
        self.logger.info('[SparkAPI.sendMessage] Message: %s' % str(payload))

        response = self.queryURL(method="POST", path="messages", payload = payload)
        return response
    