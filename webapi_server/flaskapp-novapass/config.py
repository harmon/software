import os
"""
config.py

Things specific to this instance that should be kept private
Do not commit production version to open source
"""
api_key = 'ECE22945F7A2800E'

user_db_table = """
00.00000, Pam SawUser        , sawstop:red_laser
15.30755, Joe CraftUser      , ind_sew:test:tool1:tool2:tool3:tool4:tool5
00.00002, Stewie LaserSteward, mongo:mongo_steward
"""

# master card IDs always work
all_access_card_ids_list = [
    '99.9999',
    '99.9998',
    '99.9997'
]


"""
Tool names

  * Keep short.
  * lower-case,
  * Use '_', not '-'
  * Multiple devices should be named foo, foo2, foo3, foo4

"""
tool_names = ['test', 'mongo', 'red_laser', 'sawstop', 'ind_sew']

"""
USER DB

card_id  user_name            auths
fc.nnnn, Pam SawUser        , sawstop:red_laser

where:

  card_id   : probably a hex number representing an 8 bit facility code and a 16 bit card code
  user_name : FirstName LastName of user.
  auths     : name of tools user is authorized. colon delimited Special case - <machine name>_steward
            : refers to someone who can grant access to others

"""

user_db_table = """
00.00000, Pam SawUser        , sawstop:red_laser
15.30755, Joe CraftUser      , ind_sew:tst_tool1:tst_tool2:tst_tool3:tst_tool4:
00.00002, Stewie LaserSteward, mongo:mongo_steward
"""

# master card IDs always work
all_access_card_ids_list = [
    '99.9999',
    '99.9998',
    '99.9997'
]


# Use a Class-based config to avoid needing a 2nd file
# os.getenv() enables configuration through OS environment variables
class ConfigClass(object):
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'THIS IS AN INSECURE SECRET')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///novapass-dev.sqlite')
    # CSRF_ENABLED = True

    # # Flask-Mail settings
    # MAIL_USERNAME =           os.getenv('MAIL_USERNAME',        'email@example.com')
    # MAIL_PASSWORD =           os.getenv('MAIL_PASSWORD',        'password')
    # MAIL_DEFAULT_SENDER =     os.getenv('MAIL_DEFAULT_SENDER',  '"MyApp" <noreply@example.com>')
    # MAIL_SERVER =             os.getenv('MAIL_SERVER',          'smtp.gmail.com')
    # MAIL_PORT =           int(os.getenv('MAIL_PORT',            '465'))
    # MAIL_USE_SSL =        int(os.getenv('MAIL_USE_SSL',         True))

    # # Flask-User settings
    # USER_APP_NAME        = "AppName"                # Used by email templates

    # USER_SEND_PASSWORD_CHANGED_EMAIL = False
    # USER_SEND_REGISTERED_EMAIL = False
    # USER_SEND_USERNAME_CHANGED_EMAIL = False
