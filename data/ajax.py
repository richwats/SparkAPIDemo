### AJAX FUNCTIONS ###

from flask import current_app, jsonify, session, flash
from spark import SparkAPI


## Import Forms ###
import forms


def clearSession(formData):
    current_app.logger.info('[ajax.clearSession] Clear Session')
    session.clear()
    return dict(sessionCleared = True)

def selectTeam(formData):
    current_app.logger.info('[ajax.selectTeam] Selecting Team: %s' % str(formData.get('teamName')))
    
    ## Get SparkAPI ##
    sparkAPI = SparkAPI(current_app.logger)
    response = sparkAPI.selectTeam(formData.get('teamId'),formData.get('teamName'))
    flash('Team "%s" Selected' % str(response['json']['teamName']),'success')
    return response

def chatLogin(formData):
    ### Get Form Object by Name
    
    ## used?
    current_app.logger.info('[ajax.chatLogin] Form Data: %s' % str(formData))
    chatLoginForm = forms.ChatLogin(formData)
    current_app.logger.info('[ajax.chatLogin] Login Form: %s' % str(chatLoginForm.data))
    return dict()