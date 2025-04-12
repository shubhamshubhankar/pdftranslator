import boto3
import json
import logging
import os 

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("TextTranslator function started")
    logger.info(f"Event received: {json.dumps(event)}")
    
    try:
        # Initialize clients
        translate = boto3.client('translate')
        s3 = boto3.client('s3')
        dynamodb = boto3.resource('dynamodb')
        
        # Parse SQS message
        record = event['Records'][0]
        message = json.loads(record['body'])
        logger.info(f"Processing message: {message}")
        
        # 1. Translate text
        logger.info(f"Translating text (length: {len(message['text'])})")
        result = translate.translate_text(
            Text=message['text'],
            SourceLanguageCode='en',
            TargetLanguageCode='it'
        )
        translated_text = result['TranslatedText']
        logger.info("Translation completed successfully")
        
        # 2. Save to S3
        bucket_name = os.environ['BUCKET_NAME']
        output_key = f"translated_{message['request_id']}.txt"
        logger.info(f"Saving translation to S3: {output_key}")
        s3.put_object(
            Bucket=bucket_name,
            Key=output_key,
            Body=translated_text
        )
        logger.info("Translation saved to S3")
        
        # Generate pre-signed download URL (valid for 24 hours)
        """
        download_url = s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': 'translations-417404104136',
                'Key': output_key
            },
            ExpiresIn=86400
        )
        """
        # 3. Update DynamoDB — now includes translated_text
        logger.info("Updating DynamoDB status")
        table_name = os.environ['TABLE_NAME']
        dynamodb.Table(table_name).update_item(
            Key={'request_id': message['request_id']},
            UpdateExpression="SET #status = :status, translated_file = :file, translated_text = :text",
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'COMPLETED',
                ':file': f"s3://{table_name}/{output_key}",
                ':text': translated_text
            }
        )
        logger.info("DynamoDB updated successfully")
        
        return {'status': 'success'}
        
    except Exception as e:
        logger.error(f"Error in translation: {str(e)}", exc_info=True)
        raise e
