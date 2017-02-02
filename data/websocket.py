from flask_socketio import Namespace, emit
from flask import current_app,session,request

from spark import SparkAPI, SparkMessage

import os

class SparkChatNamespace(Namespace):
    
    sparkAPI = None
    sparkSpace = None
    avatarURL = os.environ.get('SPARK_INT_AVATAR_URL')
    
    def on_connect(self):
        if 'email' not in session.keys():
            current_app.logger.info('[SparkChatNamespace.connect] Client Not Logged In - Disconnecting')
            self.disconnect(request.sid)
        else:
            current_app.logger.info('[SparkChatNamespace.connect] Client: %s Connected' % str(session['email']))
            
            ## Get SparkAPI ##
            self.sparkAPI = SparkAPI(current_app.logger)
            
            ## Get/Build Space ##
            email = session['email']
            spaceName = self.sparkAPI.buildSpaceName(email)
            current_app.logger.debug('[SparkChatNamespace] Space Name: %s' % str(spaceName))
            self.sparkSpace = self.sparkAPI.getSpaceByName(spaceName)
            current_app.logger.debug('[SparkChatNamespace] Space: %s' % str(self.sparkSpace))
            
            ## Get/Build Webhook ##
            self.sparkWebhook = self.sparkAPI.registerWebhook( self.sparkSpace['id'], email )
            #current_app.logger.debug('[SparkChatNamespace] Space: %s' % str(self.sparkWebhook))
            
            ## Send Connect Message to Room ##
            msg = SparkMessage()
            msg.roomId = self.sparkSpace['id']
            msg.markdown = "#####Web Chat - %s %s %s %s %s Connected" % (session['title'], session['firstName'],session['lastName'],session['email'],session['mobile'])
            response = self.sparkAPI.sendMessage(msg)
            current_app.logger.debug('[SparkChatNamespace.message] Message Response: %s' % str(response))
            
            emit('alert', {'message':'Client Connected'})
            response = {'text':'Welcome to the live chat.  Please type your question below.','avatar': self.avatarURL}
            emit('message', response)
        return

    def on_disconnect(self):
        current_app.logger.info('[SparkChatNamespace.disconnect] Client Disconnected')
        
        ## Send Connect Message to Room ##
        msg = SparkMessage()
        msg.roomId = self.sparkSpace['id']
        if 'email' in session.keys():
            msg.markdown = "#####Web Chat - %s %s %s %s %s Disconnected" % (session['title'], session['firstName'],session['lastName'],session['email'],session['mobile'])
            response = self.sparkAPI.sendMessage(msg)
            current_app.logger.debug('[SparkChatNamespace.disconnect] Message Response: %s' % str(response))
        else:
            current_app.logger.debug('[SparkChatNamespace.disconnect] No Session Data')
        
        return
        
    def on_message(self, data):
        current_app.logger.info('[SparkChatNamespace.message] Message: %s' % str(data))
        
        ## Add Form Submission as Message ##
        msg = SparkMessage()
        msg.roomId = self.sparkSpace['id']
        #msg.text = data
        
        ## Replace newline with double newline ##
        data = str(data).replace("\n","\n\n")
        msg.markdown = "#####Web Chat from %s %s %s %s %s\n------\n\n%s" % (session['title'], session['firstName'],session['lastName'],session['email'],session['mobile'],str(data))
        ### Spark Markdown doesn't like whitespace.. ###
        #msg.markdown = str(markdown).replace(" ","").replace("++"," ")
        
        response = self.sparkAPI.sendMessage(msg)
        current_app.logger.debug('[SparkChatNamespace.message] Message Response: %s' % str(response))
        
        #response = {'text':'You typed: %s' % str(data)}
        #emit('message', response)
        return
        
        
        

# ### SocketIO ###
# 
# @socketio.on('json')
# def handle_json(json):
#     app.logger.debug('[app.socketio.handle_json] Json: %s' % str(json))
# 
# @socketio.on('join')
# def on_join(data):
#     username = data['username']
#     room = data['room']
#     join_room(room)
#     send(username + ' has entered the room.', room=room)
# 
# @socketio.on('leave')
# def on_leave(data):
#     username = data['username']
#     room = data['room']
#     leave_room(room)
#     send(username + ' has left the room.', room=room)
# 
# @socketio.on('connect')
# def client_connect():
#     app.logger.debug('[app.socketio.client_connect] Client Connect Event')
#     emit('my response', {'data': 'Connected'})
# 
# @socketio.on('disconnect')
# def client_disconnect():
#     app.logger.debug('[app.socketio.client_connect] Client Disconnect Event')
