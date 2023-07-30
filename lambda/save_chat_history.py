import json 

def handler(event, context):
    bot_id = event['pathParameters']['bot-id']
    client_id = event['pathParameters']['client-id']
    body = json.loads(event['body'])

    return {
        'statusCode': 200,
        'headers': {
            'content-type': 'text/plain'
        },
        'body': 'received request with params: bot-id: {}, client-id: {}, body: {}'.format(bot_id, client_id, body),
    }