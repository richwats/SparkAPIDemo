from flask import Flask, render_template, request, session, flash, redirect, url_for, g, jsonify, abort

## Flask_Bootstrap ##
from flask_bootstrap import Bootstrap

## Flask_Nav ##
from nav import nav

## Flask_WTF ##
from flask_wtf.csrf import CSRFProtect
import forms

### AJAX Functions ###
import ajax

### Utility Functions ###
import utils 

### JSON ###
import json

### OrderedDict ###
from collections import OrderedDict

### RE ###
import re

### SocketIO Functions ###
#from socketio import socketio_manage
#from socketio.server import SocketIOServer
# from socketio.namespace import BaseNamespace
# from socketio.mixins import BroadcastMixin
#from websocket import Application

## Flask SocketIO ##
from flask_socketio import SocketIO, join_room, leave_room, send, emit
from websocket import SparkChatNamespace

## Config ##
import configparser

## Spark ARI ##
from spark import SparkAPI, SparkMessage

### OS ##
import os


"""
FLASK APP CONFIG
"""

## Flask 
app = Flask(__name__,
            template_folder="/app/template/",
            static_folder="/app/static"
            )

## Flask Bootstrap ##
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
app.config['BOOTSTRAP_QUERYSTRING_REVVING'] = False
Bootstrap(app)

## Flask WTF / CSRF ##
try:
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
    csrf = CSRFProtect(app)
except Exception as e:
    app.logger.error('[app] Initialisation Error: %s' % str(e))
    exit

## Flask Nav ##
nav.init_app(app)

## SocketIO ##
socketio = SocketIO(app,
                    #allow_upgrades=False,
                    logger=app.logger,
                    engineio_logger=app.logger
                    )

### Logging ###
app.logger.info('[app] App Initiated')


### Additonal Context ###
@app.context_processor
def passUtils():
    return dict(getForm = utils.getForm)

# ### Load Auth Token ###
# authFile = open('/tmp/auth_code','r')
# authCode = None
# with authFile:
#     authCode = authFile.read()
#     app.logger.debug('[app] Using Auth Code: %s' % str(authCode))


### VIEWS ###
@app.route('/')
def index():
    app.logger.info('[app.index] Rendering index.html')
    return render_template('index.html')

### WebHooks ###
@app.route('/webhook/', methods=['POST'])
@csrf.exempt
def web_hook():
    ## Webhooks are not POST Form ##
    binData = request.get_data()
    payload = binData.decode('utf-8')
    app.logger.info('[app.webhook] Webhook Received: %s' % str(payload) )
    
    jsonObj = json.loads(payload, object_pairs_hook=OrderedDict )
    #app.logger.info('[app.webhook] JSON: %s' % str(jsonObj) )
    app.logger.debug('[app.webhook] JSON Keys: %s' % str(list(jsonObj.keys())) )
    
    ### Received Webhook ###
    webhookId = jsonObj['id']
    webhookName = jsonObj['name']
    messageId = jsonObj['data']['id']
    
    ## Get SparkAPI ##
    sparkAPI = SparkAPI(app.logger)
    response = sparkAPI.getMessageById(messageId)
    
    ## Filter "Web Chat" Messages ##
    if re.search("^Web Chat", str(response['json']['text'])):
        app.logger.debug('[app.webhook] Filtering Message: %s' % str(response['json']['text']) )
        return jsonify({'results': False })
    
    ## Load Senders Details ##
    personId = response['json']['personId']
    peopleObj = sparkAPI.getPeopleDetails(personId)
    
    
    message = {
        'text': '(%s) %s' % (str(response['json']['personEmail']),str(response['json']['text'])),
        'avatar': str(peopleObj['json']['avatar'])
        }

    #response = {'text':'Message Received from Spark.'}
    socketio.emit('message', message, namespace = "/sparkchat")

    
    
    
    #selectedTeamName = sparkAPI.teamName
    
    return jsonify({'results': True })

### AJAX ###
@app.route('/ajax', methods=['POST'])
def ajaxCall():    
    app.logger.info('[app.ajax] Received AJAX Request: %s' % str(request.form))
    
    try:
        ## Set Call ##
        call = request.form.get('call')
        app.logger.debug('[app.ajax] Ajax Call: %s' % str(call))

        if hasattr(ajax, call):
            ### Call existing in Ajax Module ###
            function = getattr(ajax, call)
            app.logger.debug('[app.ajax] Function: %s' % str(function))
            results = function(request.form)
            app.logger.debug('[app.ajax] Results: %s' % str(results))
            
            # if isinstance(results, dict):
            #     if '_topLevel' in results.keys():
            #         if results['_topLevel']:
            #             #app.logger.debug('[start.ajax] Sending Top Level Results: %s' % str(results))
            #             return jsonify(results['results']);
            #     else:
            #         app.logger.debug('[start.ajax] Function Results: %s' % str(results))
            #         return jsonify({'results': results })
            # else:
            #     app.logger.debug('[start.ajax] Function Results: %s' % str(results))
            #     return jsonify({'results': results })
            
            return jsonify({'results': results })
        else:
            ### Call does not exist ###
            msg = '[app.ajax] Requested AJAX Call does not exist: %s' % str(call)
            app.logger.error(msg)
            flash(msg,'error')
            abort(501)

    except Exception as e:
        app.logger.error('[app.ajax] %s' % str(e))
        flash(str(e),'error')
        abort(501)

@app.route('/spark_auth/')
def spark_auth():
    authCode = request.args.get('code')
    authState = request.args.get('state')
    app.logger.info('[app.spark_auth] Received Spark Authorization Reponse - Code: %s State: %s' % (str(authCode),str(authState)))
    if authCode is not None:
        
        ## Retrieve Access Tokens ##
        sparkAPI = SparkAPI(app.logger)
        results = sparkAPI.setAccessToken(authCode)
        
        app.logger.debug('[app.spark_auth] Access Token Results: %s' % str(results))
        
        ## Store Codes ##
        config = configparser.ConfigParser()
        config['AUTH CODE'] = {'authCode': authCode,
                               'authState': authState
                               }
        config['ACCESS TOKEN'] = {'access_token': results['access_token'],
                                  'expires_in': results['expires_in'],
                                  'refresh_token': results['refresh_token'],
                                  'refresh_token_expires_in': results['refresh_token_expires_in']
                               }

        with open('/tmp/config.ini', 'w') as configfile:
            config.write(configfile)
            configfile.close()
        

        ## Test Code ##
        config = configparser.ConfigParser()
        config.read('/tmp/config.ini')
        authCode = config['AUTH CODE']['authCode']
        access_token = config['ACCESS TOKEN']['access_token']
        app.logger.debug('[app.spark_auth] Written Auth Code: %s' % str(authCode))
        app.logger.debug('[app.spark_auth] Written Access Token: %s' % str(access_token))
        flash('Spark Authorization Successful','success')
    else:
        flash('Spark Authorization Failed','danger')    
    return redirect(url_for('index'))



@app.route('/spark_team/', methods=['GET','POST'])
def spark_team():
    app.logger.info('[app.about_us] Rendering spark_team.html')
    ## Get SparkAPI ##
    sparkAPI = SparkAPI(app.logger)
    selectedTeamName = sparkAPI.teamName
    
    if selectedTeamName is None:
        flash('Warning: No Cisco Spark Team Selected. New Rooms will not be added unless a Team is selected.','warning')
    
    ## Build Add New Team Form ##
    newTeamForm = forms.NewTeam()
    
    ## Get List of Spark Teams ##
    teamList = None
    teamList = sparkAPI.listTeams()
    
    
    ## Process Add New Team Form ##
    if newTeamForm.validate_on_submit():
        app.logger.info('[app.spark_team] Form Data Validated: %s' % str(newTeamForm.data))
        
        ## Add New Team ##
        try:
            teamName = newTeamForm.teamName.data
            app.logger.debug('[app.spark_team] New Team Name: %s' % str(teamName))
            response = sparkAPI.createTeam(teamName)
            flash('New Team "%s" Successfully Created' % str(response['json']['name']),'success')
            
            ## Select New Team ##
            teamId = response['json']['id']
            response = sparkAPI.selectTeam(teamId, teamName)
            flash('Team "%s" Selected' % str(response['json']['teamName']),'success')
            
            return redirect(url_for('spark_team'))
        
        except Exception as e:
            app.logger.error('[app.spark_team] %s' % str(e))
            flash(str(e),'error')
    
    
    renderDict = {
        'teamList': teamList,
        'selectedTeamName': selectedTeamName,
        'newTeamForm': newTeamForm
    }
    
    return render_template('spark_team.html', **renderDict )

@app.route('/about_us/')
def about_us():
    app.logger.info('[app.about_us] Rendering about_us.html')
    return render_template('about_us.html')

@app.route('/spark/')
def spark():
    app.logger.info('[app.spark] Rendering spark.html')
    return render_template('spark.html')



@app.route('/contact_us/', methods=['GET','POST'])
def contact_us():
    app.logger.info('[app.contact_us] Rendering contact_us.html')
    
    
    
    ## Init Form ##
    contactForm = forms.ContactUs()
    
    ## Process Contact Us Form ##
    if contactForm.validate_on_submit():
        app.logger.info('[app.contact_us] Form Data Validated: %s' % str(contactForm.data))
        
        ## Get SparkAPI ##
        try:
            sparkAPI = SparkAPI(app.logger)
            spaceName = sparkAPI.buildSpaceName(contactForm.email.data)
            app.logger.debug('[app.contact_us] Space Name: %s' % str(spaceName))
            space = sparkAPI.getSpaceByName(spaceName)
            app.logger.debug('[app.contact_us] Space: %s' % str(space))
            
            ## Add Form Submission as Message ##
            msg = SparkMessage(text = None)
            msg.roomId = space['id']
            #msg.markdown = '''## Form Submission\n\n### Details\n\n* Email Address: %s\n* First Name: %s\n* Last Name: %s\n* Mobile: %s\n\n### Message\n\n------\n\n%s''' % (contactForm.email.data, contactForm.firstname.data, contactForm.lastname.data, contactForm.mobile.data, contactForm.message.data)
            markdown = '''## Form++Submission
            
            ### Details
            
            *++Name:++%s++%s++%s
            *++Email++Address:++%s
            *++Mobile:++%s
            
            ### Message
            
            ------
            
            ''' % (contactForm.title.data,
                   str(contactForm.firstname.data).capitalize(),
                   str(contactForm.lastname.data).capitalize(),
                   contactForm.email.data,
                   contactForm.mobile.data
                   )
            ### Spark Markdown doesn't like whitespace.. ###
            msg.markdown = str(markdown).replace(" ","").replace("++"," ")
            msg.markdown = "%s%s" % (str(msg.markdown),str(contactForm.message.data))
            response = sparkAPI.sendMessage(msg)
            app.logger.debug('[app.contact_us] Message Response: %s' % str(response))
            
        except Exception as e:
            app.logger.error('[app.contact_us] %s' % str(e))
            flash(str(e),'error')
    
        ### Get Spark Space/Room ###
        
        flash('Form Successfully Submitted','success')
        return redirect(url_for('index'))
    
    return render_template('contact_us.html', contactForm = contactForm )

@app.route('/loadModal/<modalName>/', methods=['GET','POST'])
def loadModal(modalName, formName = None):
    app.logger.info('[app.loadModal] Rendering Modal Name: %s' % str(modalName))
    
    if modalName == "chatModal":
        ## Check Session ##
        if 'email' in session.keys():
            ## Logged In ##
            app.logger.info('[app.loadModal] Rendering Chat Window - User Email: %s' % str(session['email']))
            path = '/modal/chatWindow.html'
            return render_template(path)
        else:
            ## Display Login Form ##
            formName = "ChatLogin"
            app.logger.info('[app.loadModal] Rendering Form Name: %s' % str(formName))
            
            ## Form Instance ##
            if request.method == "POST":
                formInstance = utils.getForm(formName, request.form)
                
                if formInstance.validate_on_submit():
                    ## Form Validates ##
                    if formName == "ChatLogin":
                        app.logger.debug('[app.loadModal] Validated Form Data: %s' % str(formInstance.data))
                        session['title'] = formInstance.title.data
                        session['firstName'] = str(formInstance.firstname.data).capitalize()  # lowercase
                        session['lastName'] = str(formInstance.lastname.data).capitalize() # lowercase
                        session['email'] = formInstance.email.data
                        session['mobile'] = formInstance.mobile.data
                    
                        path = '/modal/chatLoginSuccessful.html'
                        return render_template(path)
                else:
                    ## Form Invalid ##
                    #app.logger.debug('[app.loadModal] Invalid Form Data: %s' % str(formInstance.data))
                    app.logger.debug('[app.loadModal] Invalid Form - Errors: %s' % str(formInstance.errors))
                
            else:
                formInstance = utils.getForm(formName)
            
            ## Render Dictionary ##
            renderDict = dict()
            renderDict[formName] = formInstance
        
            path = '/modal/chatLogin.html'
            return render_template(path, **renderDict)
    
    else:
        app.logger.error('[app.loadModal] Modal Not Defined: %s' % str(modalName))
        return redirect(url_for('index'))

# @app.route('/register', methods=['GET','POST'])
# def register():
#     app.logger.info('[app.register] Rendering register.html')
#     
#     ## Init Form ##
#     registerForm = forms.RegisterUser()
#     
#     ## Process Register Form ##
#     if registerForm.validate_on_submit():
#         app.logger.info('[app.register] Form Data Validated: %s' % str(register.data))
#         
#         ## Add User Function ##
#         ## Register user to Spark...
#         
#         flash('User has been successfully registered','success')
#         return redirect(url_for('index'))
#     
#     return render_template('register.html', registerForm = registerForm )

# @socketio.on('connect')
# def client_connect():
#     app.logger.debug('[app.socketio] Client Connect Event')
#     #emit('message', {'data': 'Connected'})
#     return 'one', 2
# 
# @socketio.on('disconnect')
# def client_disconnect():
#     app.logger.debug('[app.socketio] Client Disconnect Event')
#     return 'one', 2


### Run Flask App in Debug ###

if __name__ == '__main__':
    host = '0.0.0.0'
    httpPort = 8080  ## Container Local
    webSocketPort = 5000 ## Container Local
    #policyPort = 10843 ## Container Local
    
    ## Flask ##
    #app.run(debug=True, host=host, port=httpPort)
    
    ## SocketIO ##
    socketio.on_namespace(SparkChatNamespace('/sparkchat'))
    socketio.run(app, host=host, port=httpPort,debug=True,use_reloader=True)
    
    
    # ## SocketIO ##
    # server = SocketIOServer(
    #     (host, webSocketPort),
    #     Application(),
    #     resource="socket.io",
    #     policy_server=True,
    #     policy_listener=(host, policyPort)
    #     )
    # server.serve_forever()
    # 
    