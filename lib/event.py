import json

def parseEvent(event):
    if 'Records' in event:
        return {
            'type': 'sns',
            'payload': json.loads(event['Records'][0]['Sns']['Message']),
        };

    else:
        return {
            'type': 'http',
            'payload': event,
        }

    raise Exception('Unknown event type')