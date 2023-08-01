import os
import json
import boto3
from datetime import datetime
from typing import Any, Dict
from botocore.exceptions import BotoCoreError, ClientError
from pydantic import BaseModel

s3 = boto3.client('s3')
bucket_name = os.environ['BUCKET_NAME']  # This should be set as an environment variable when deploying the function

class ChatContent(BaseModel):
    conversation_id: str
    timestamp: str
    content: str

def handler(event: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    try:
        body = json.loads(event.get('body', '{}'))
        chat_content = ChatContent(**body)

        conversation_id = chat_content.conversation_id
        timestamp = chat_content.timestamp
        content = chat_content.content
        bot_id = event['pathParameters']['bot_id']
        client_id = event['pathParameters']['client_id']
        

        current_date = datetime.now().strftime("%Y-%m-%d")
        filename = f"{current_date}_{conversation_id}.txt"
        key = f"{bot_id}/{client_id}/{filename}"

        data = f"{timestamp}: {content}\n"

        try:
            # Try to append to the existing object
            response = s3.get_object(Bucket=bucket_name, Key=key)
            existing_data = response['Body'].read().decode()
            data = existing_data + data
        except (BotoCoreError, ClientError):
            # The object does not exist, we will create it
            pass

        try:
            s3.put_object(Body=data, Bucket=bucket_name, Key=key)
            return {
                'statusCode': 201,
                'headers': {
                    'content-type': 'text/plain'
                },
                'body': f'Successfully created or updated {key}\n'
            }
        except (BotoCoreError, ClientError) as error:
            return {
                'statusCode': 422,
                'headers': {
                    'content-type': 'text/plain'
                },
                'body': f'Could not create or update {key}: {str(error)}\n'
            }
    except ValueError as ve:
        return {
            'statusCode': 400,
            'body': str(ve)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }        