import json 

def handler(event, context):
    print('request {}'.format(json.dumps(event)))

    return {
        'statusCode': 200,
        'headers': {
            'content-type': 'text/plain'
        },
        'body': 'Test body'
    }