import boto3
import json
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:        
        logger.info(f"Query params: {event.get('queryStringParameters')}")

        # Get request_id from query string
        request_id = event.get('queryStringParameters', {}).get('request_id')
        
        if not request_id:
            logger.error("No request_id provided")
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': '*'
                },
                'body': json.dumps({'error': 'request_id is required'})
            }

        # Append '.pdf' to match key in DynamoDB
        full_request_id = f"{request_id}.pdf"
        logger.info(f"Checking status for: {full_request_id}")
        
        # Query DynamoDB
        table_name = os.environ['TABLE_NAME']
        resource_name = os.environ['RESOURCE_NAME']

        dynamodb = boto3.resource(resource_name)
        response = dynamodb.Table(table_name).get_item(
            Key={'request_id': full_request_id},
            ConsistentRead=True
        )
        
        if 'Item' not in response:
            logger.warning(f"No record found for: {full_request_id}")
            return {
                'statusCode': 404,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': '*'
                },
                'body': json.dumps({'error': 'Request not found'})
            }
        
        item = response['Item']
        logger.info(f"Found record: {json.dumps(item, indent=2)}")

        # Extract only required fields
        filtered_response = {
            'status': item.get('status'),
            'translated_text': item.get('translated_text', '')
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps(filtered_response)
        }

    except Exception as e:
        logger.error(f"Error checking status: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
