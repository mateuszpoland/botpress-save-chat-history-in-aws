import os
import json
import boto3
from datetime import datetime
from typing import Any, Dict
from botocore.exceptions import BotoCoreError, ClientError
from pydantic import BaseModel, ValidationError
import logging

s3 = boto3.client('s3')
bucket_name = os.environ['BUCKET_NAME']  # This should be set as an environment variable when deploying the function
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

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
            response = s3.put_object(Body=data, Bucket=bucket_name, Key=key)
            logger.info(f"Response from S3: {response}")  # Log the response from S3
            return {
                'statusCode': 201,
                'headers': {
                    'content-type': 'application/json',
                },
                'body': json.dumps({'msg': f'Successfully created or updated {key}'})
            }
        except (BotoCoreError, ClientError, Exception) as error:
            logger.error(f"Error error: {error}")
            return {
                'statusCode': 422,
                'headers': {
                    'content-type': 'application/json'
                },
                'body': json.dumps({'msg': f'Could not create or update {key}: {str(error)}'})
            }
    except (ValueError, ValidationError) as ve:
        logger.error(f"Value error: {ve}")
        return {
            'statusCode': 400,
            'body': str(ve)
        }
    except Exception as e:
        logger.error(f"Unknown error: {e}")
        return {
            'statusCode': 500,
            'body': str(e)
        }        