# 📝 PDF Translator – Serverless Application on AWS

This project enables users to upload PDF files and receive translations in Italian using a fully serverless architecture powered by AWS.

---

## 🚀 Live Demo

Frontend: [PDF Translator Web](https://d1d3fusiyjat60.cloudfront.net/)

---

## 📐 Architecture Overview

The system is built with modular Lambda functions and event-driven services for scalability and fault tolerance:

1. **Frontend**: Uploads PDF to S3 via a pre-signed URL (from API Gateway + Lambda)
2. **PDF Upload Trigger**: S3 event invokes a Lambda function to extract text
3. **Text Extraction**: Lambda function extracts and stores text in DynamoDB
4. **Queue**: Adds a message to an SQS queue for translation
5. **Translation Lambda**: Translates text and stores result in S3
6. **Status Checking**: API Gateway + Lambda allows polling job status

---

## 🧱 AWS Services Used

### 🗂 S3 Buckets
- Store uploaded PDFs
- Store translated outputs
- Host static frontend website

### 🧠 Lambda Functions
- Generate pre-signed upload URL
- Extract text from PDF
- Translate extracted text
- Return job status and result

### 📨 Amazon SQS
- Triggers translation workflow asynchronously

### 📘 DynamoDB
Stores information regarding the status of the process.

### 🌐 API Gateway
REST endpoints to:
- Get upload URL
- Check status of submitted jobs
