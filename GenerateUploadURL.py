import boto3
import json
import os

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    
    # Generate unique ID for the file
    request_id = context.aws_request_id

    bucket_name = os.environ['UPLOAD_BUCKET']

    # Generate pre-signed URL (expires in 1 hour)
    url = s3.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': bucket_name,  # Replace with your bucket name
            'Key': f"{request_id}.pdf"
        },
        ExpiresIn=3600
    )
    
    # Return the response with the URL and request ID as a JSON object
    return {
        'statusCode': 200,
        'body': json.dumps({
            'url': url,
            'request_id': request_id
        })
    }
