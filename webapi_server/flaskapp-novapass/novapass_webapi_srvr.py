import config  # make good on what we just explained
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import logging
# for creating self-managing log files
from logging.handlers import TimedRotatingFileHandler
from logging import Formatter  # for setting logger formats

import sys  # for stderr.write
import socket  # for gethostname

"""

Web API Server for RFID Access Card Readers

bob@cogwheel.com

Notes here: https://goo.gl/wGexz4

"""

"""
constants and localizations are kept in

config.py

Which will contain the following:

    API KEY

        api_key = '<shared key>' # a random 16 char hex number the readers send along with queries

    example

        api_key = 'dead89022abcd9876'

    USER DB

        a heredoc csv table containing records with the following

          card_id   : probably a hex number representing an 8 bit facility code and a 16 bit card code
          user_name : FirstName LastName of user.
          auths     : name of tools user is authorized. colon delimited Special case - <machine name>_steward
                    : refers to someone who can grant access to others. Keep them short, lower case, use '_' todelimit words

    example

        user_db_table=\"\"\"
        00.00000, Pam SawUser        , sawstop:red_laser
        15.30755, Joe CraftUser      , ind_sew:test:tool1:tool2:tool3:tool4:tool5:
        00.00002, Stewie LaserSteward, mongo:mongo_steward
        \"\"\"

    MASTER CARD IDS

        Hard-coded card ids which work always

     example

            all_access_card_ids_list = [ '99.9999', '99.9998', '99.9997'  ]

    TOOL NAMES

      * Keep short.
      * lower-case,
      * Use '_', not '-'
      * Multiple devices should be named foo, foo2, foo3, foo4

    example

        tool_names = [ 'test', 'mongo', 'red_laser', 'sawstop', 'ind_sew' ]

"""

api_key = config.api_key
tool_names = config.tool_names
user_db_table = config.user_db_table
all_access_card_ids_list = config.all_access_card_ids_list


def get_user_db():
    # takes the users in the heredoc format and returns them as array
    global user_db_table
    user_db_lines = user_db_table.split('\n')
    user_db_parsed = []
    for line in user_db_lines:
        fields = line.split(',')
        if (len(fields) == 3):
            for i in range(0, len(fields)):
                # clean up multiple spaces
                fields[i] = ' '.join(fields[i].split())
                # sys.stderr.write('['+fields[i]+']' + '\n')

            user_db_parsed.append(fields)
    return(user_db_parsed)


def auth_respond(error=0, message='', user_name='', tool_auths=''):
    global logger
    logger.info('error:' + str(error) + ', message:' + message +
                ', user_name:' + user_name + ', tool_auths:' + tool_auths)
    return({'error': error, 'message': message, 'user_name': user_name, 'tool_auths': tool_auths})


def log_respond(error, message):
    global logger
    logger.info('error:' + str(error) + ', message:' + message)
    return({'error': error, 'message': message})


def getauth_from_db(args):
    """
    Look up card id in DB and determines if access should be granted
    returns json message that can be sent directly to client.
    """
    global logger
    global tool_names

    print args
    print api_key

    if (args['api_key'] != api_key):
        logger.info('api_key invalid')
        return auth_respond(1, 'api_key invalid', '')

    if args['card_id'] in all_access_card_ids_list:
        # found in all_access_card_ids_list. Grant access
        logger.info('granted: all_access_card')
        return auth_respond(0, 'granted: all_access_card', '')
    else:
        #
        # search db for card id
        #
        user_db_parsed = get_user_db()
        found_card_id = found_tool_auth = False
        for u in user_db_parsed:
            (db_card_id, db_user_name, db_tool_auths) = u
            if (db_card_id == args['card_id']):
                #
                # if we found the card id
                #
                found_card_id = True
                db_tool_auth_list = db_tool_auths.split(':')

                for db_tool in db_tool_auth_list:
                    if db_tool == args['tool_id']:
                        found_tool_auth = True
                        #
                        # and they are authorized
                        #
                        logger.info('getauth_from_db: found record. ' +
                                    ' db_card_id:' + db_card_id +
                                    ', user_name:' + db_user_name +
                                    ', tool_auths:' + db_tool_auths
                                    )
                        #
                        # then grant access
                        #
                        return auth_respond(0, 'granted', db_user_name, db_tool_auths)

    if (not found_card_id):
        return auth_respond(1, 'denied: unknown card', '')
    if (not found_tool_auth):
        return auth_respond(1, 'denied: not authorized', '')

    return auth_respond(1, 'error: badly-formed request')


def getauth_process():
    """
    RESTful calls from readers asking for card authorization come here
    """
    global logger
    global request

    p = reqparse.RequestParser()

    # answer when requested as json in a post
    p.add_argument('tool_id', type=str, location='json')
    p.add_argument('api_key', type=str, location='json')
    p.add_argument('card_id', type=str, location='json')

    # answer when requested on url
    # p.add_argument('rdr_id',type=str)
    # p.add_argument('api_key',type=str)
    # p.add_argument('card_id',type=str)

    # get passed params
    args = p.parse_args()

    # logger.info('getauth ' + 'ip:' + request.remote_addr + ' api_key:' + args['api_key'])
    # logger.info('getauth ' + ' card_id:' + args['card_id'])

    args.setdefault('api_key', '')
    args.setdefault('card_id', '')
    args.setdefault('tool_id', '')

    return(getauth_from_db(args))


def setup_logger():

    global logger

    logger.setLevel(logging.DEBUG)
    if (socket.gethostname() == 'srv-a.nova-labs.org'):
        log_file_path = '/var/log/novapass/'
    else:
        app.debug = True
        log_file_path = './logs/'

    loghandler = TimedRotatingFileHandler(
        log_file_path + '/log', when="W0", interval=1, backupCount=52)

    loghandler.setFormatter(Formatter('%(asctime)s: %(message)s '))

    logger.addHandler(loghandler)
    logger.addHandler(logging.StreamHandler())
    logger.info(__name__ + ': Startup')
    sys.stderr.write(__name__ + ': Logging going to ' + log_file_path + '/log')


def log_process():
    """
    RESTful calls from readers wanting to log come here
    """
    global logger

    p = reqparse.RequestParser()

    # answer when requested as json in a post
    p.add_argument('tool_id', type=str, location='json')
    p.add_argument('api_key', type=str, location='json')
    p.add_argument('message', type=str, location='json')

    # get passed params
    args = p.parse_args()

    args.setdefault('api_key', '')
    args.setdefault('message', '')
    args.setdefault('tool_id', '')

    if (args['api_key'] != api_key):
        return log_respond(1, 'api_key invalid')

    logger.info('tool_id:' + args['tool_id'] + ',' + args['message'])

    return log_respond(0, 'ok: log posted')


class GetAuthRest(Resource):
    # /getauth/ queries come here

    def get(self):
        return getauth_process()

    def post(self):
        return getauth_process()


class LogRest(Resource):
    def post(self):
        return log_process()

# ----- setup basic flask app
app = Flask(__name__)
api = Api(app)
logger = logging.getLogger()

setup_logger()
api.add_resource(GetAuthRest, '/novapass/api/v1.0/getauth',
                 endpoint='getauth')
api.add_resource(LogRest, '/novapass/api/v1.0/log', endpoint='log')
sys.stderr.write('Starting up')

if __name__ == '__main__':  # only applicable if we are invoked from command line:
    app.run(host="0.0.0.0", port=1916, debug=True)
