'''
Wrappers for the standard logging module classes
'''

from __future__ import absolute_import


import logging

__all__ = []


__all__.append('DriplineLogger')
class DriplineLogger(logging.Logger):
    '''
    Custom Logger for use in dripline modules.
    '''
    def notice(self, msg, *args, **kwargs):
        '''
        notice provides an extra logging level between info and warning.
        '''
        self.log(level=25, msg=msg, *args, **kwargs)


__all__.append('SlackHandler')
class SlackHandler(logging.Handler):
    '''
    A custom handler for sending messages to slack
    '''
    def __init__(self, *args, **kwargs):
        logging.Handler.__init__(self, *args, **kwargs)
        try:
            import slackclient
            import json
            slack = json.loads(open('/home/laroque/.project8_authentications.json').read())['slack']
            if 'dripline' in slack:
                token = slack['dripline']
            else:
                token = slack['token']
            self.slackclient = slackclient.SlackClient(token)
        except ImportError as err:
            if 'slackclient' in err.message:
                logger.warning('The slackclient package (available in pip) is required for using the slack handler')
            raise


__all__.append('TwitterHandler')
class TwitterHandler(logging.Handler):
    '''
    A custom message handler for redirecting text to twitter
    '''
    def emit(self, record):
        try:
            import TwitterAPI, yaml, os
            auth_kwargs = yaml.load(open(os.path.expanduser('~/.twitter_authentication.yaml')))
            api = TwitterAPI.TwitterAPI(**auth_kwargs)
            tweet_text = '{} #SCAlert'.format(self.format(record)[:100])
            api.request('statuses/update', {'status': tweet_text})
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
