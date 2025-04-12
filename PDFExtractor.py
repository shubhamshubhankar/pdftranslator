import boto3
import PyPDF2
import io
import json
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("PDFExtractor function started")
    logger.info(f"Event received: {json.dumps(event)}")
    
    try:
        # Initialize clients
        s3 = boto3.client('s3')
        dynamodb = boto3.resource('dynamodb')
        sqs = boto3.client('sqs')
        
        # Get file details
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
        logger.info(f"Processing file: s3://{bucket}/{key}")
        
        # 1. Download PDF
        logger.info("Downloading PDF from S3")
        response = s3.get_object(Bucket=bucket, Key=key)
        pdf_file = io.BytesIO(response['Body'].read())
        logger.info("PDF downloaded successfully")
        
        # 2. Extract text
        logger.info("Extracting text from PDF")
        reader = PyPDF2.PdfReader(pdf_file)
        text = "\n".join([page.extract_text() for page in reader.pages])
        logger.info(f"Extracted {len(text)} characters from PDF")
        logger.info(f"The text is : {text}")
        
        # 3. Update DynamoDB
        logger.info("Updating DynamoDB status")
        table_name = os.environ['TABLE_NAME']
        dynamodb.Table(table_name).update_item(
            Key={'request_id': key},
            UpdateExpression="SET #status = :status, extracted_text = :text",
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'EXTRACTED',
                ':text': text
            }
        )
        logger.info("DynamoDB updated successfully")
        
        # 4. Send to SQS
        logger.info("Sending message to SQS")
        query_url = os.environ['QUERY_URL']
        sqs.send_message(
            QueueUrl=query_url,
            MessageBody=json.dumps({
                'request_id': key,
                'text': text,
                'bucket': bucket
            })
        )
        logger.info("Message sent to SQS successfully")
        
        return {'status': 'success'}
        
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}", exc_info=True)
        raise e