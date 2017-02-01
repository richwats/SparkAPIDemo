### Python Flask-Nav Navbar Definition ###
from flask import Flask

## Flask_Nav ##
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator

nav = Nav()

nav.register_element('main_top',
        Navbar(
            'Acme Sparkplugs Corporation',
            View('Home', 'index'),
            View('About Us', 'about_us'),
            View('Contact Us', 'contact_us'),
            Subgroup(
                'Admin',
                View('Spark Authorization', 'spark'),
                View('Spark Team', 'spark_team')
                )
            # Subgroup(
            #     'Docs',
            #     Link('Flask-Bootstrap', 'http://pythonhosted.org/Flask-Bootstrap'),
            #     Link('Flask-AppConfig', 'https://github.com/mbr/flask-appconfig'),
            #     Link('Flask-Debug', 'https://github.com/mbr/flask-debug'),
            #     Separator(),
            #     Text('Bootstrap'),
            #     Link('Getting started', 'http://getbootstrap.com/getting-started/'),
            #     Link('CSS', 'http://getbootstrap.com/css/'),
            #     Link('Components', 'http://getbootstrap.com/components/'),
            #     Link('Javascript', 'http://getbootstrap.com/javascript/'),
            #     Link('Customize', 'http://getbootstrap.com/customize/'), ),
            #     #Text('Using Flask-Bootstrap {}'.format(FLASK_BOOTSTRAP_VERSION)),
        )
    )