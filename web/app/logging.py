from logging import Handler, Formatter
import requests
import json

class SendGridHandler(Handler):
    def __init__(self, apikey, to_addrs, from_addr):
        self.host = 'https://api.sendgrid.com/v3/'
        self.apikey = apikey
        self.to_addrs = to_addrs
        self.from_addr = from_addr
        super(SendGridHandler, self).__init__()

    def emit(self, record):
        data = {
            'personalizations': [{
                'to': [{
                    'email': self.to_addrs}],
                    'subject': 'Crash report'}],
            'from': { 'email': self.from_addr},
            'content': [{
                'type': 'text/plain',
                'value': self.format(record)}]}

        return requests.post('{host}mail/send'.format(host=self.host),
                             json.dumps(data),
                             headers={'Authorization': 'Bearer {apikey}'.format(apikey=self.apikey),
                                      'Content-type': 'application/json'}).json
