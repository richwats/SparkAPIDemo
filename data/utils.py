### UTILITY FUNCTIONS ###
from flask import current_app

## Forms ##
import forms

### Build Form Functions ###
def getForm(formName, valDict=dict()):
    ### Get Form Object by Name
    current_app.logger.info('[forms.getForm] Form Name: %s' % str(formName))
    if hasattr(forms, str(formName)):
        formType = getattr(forms, str(formName))
        form = formType()
        
        current_app.logger.info('[forms.getForm] Value Dictionary: %s' % str(valDict))
        for key in valDict.keys():
            form[key].data = valDict[key]
        
        return form
    else:
        error = '[forms.getForm] Error: %s not Found' % str(formName)
        current_app.logger.error(error)
        raise(Exception(error))
