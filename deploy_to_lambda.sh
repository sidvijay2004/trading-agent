#!/bin/bash

# Configurable variables
FUNCTION_NAME="dailySentimentBotContainer"
ECR_REPO_NAME="trading-lambda"
IMAGE_TAG="latest"
AWS_REGION="us-east-2"
EXECUTION_ROLE_NAME="lambda-container-exec-role"

# Get account and role info
ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)
ECR_URI="$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME"
ROLE_ARN="arn:aws:iam::$ACCOUNT_ID:role/$EXECUTION_ROLE_NAME"

echo "🚀 Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URI

echo "📦 Creating ECR repo if needed..."
aws ecr describe-repositories --repository-names $ECR_REPO_NAME --region $AWS_REGION >/dev/null 2>&1 || \
aws ecr create-repository --repository-name $ECR_REPO_NAME --region $AWS_REGION

echo "🐳 Building and pushing Docker image to ECR..."
# Disable BuildKit for Lambda compatibility
DOCKER_BUILDKIT=0 docker build --platform linux/amd64 -t $ECR_URI:$IMAGE_TAG .
docker push $ECR_URI:$IMAGE_TAG

echo "🔍 Checking if Lambda function exists..."
if aws lambda get-function --function-name $FUNCTION_NAME --region $AWS_REGION >/dev/null 2>&1; then
  echo "🔁 Function exists. Updating image..."
  aws lambda update-function-code \
    --function-name $FUNCTION_NAME \
    --image-uri $ECR_URI:$IMAGE_TAG \
    --region $AWS_REGION
else
  echo "🆕 Creating new Lambda function..."
  aws lambda create-function \
    --function-name $FUNCTION_NAME \
    --package-type Image \
    --code ImageUri=$ECR_URI:$IMAGE_TAG \
    --role $ROLE_ARN \
    --region $AWS_REGION \
    --timeout 900 \
    --memory-size 1024
fi

echo "✅ Deployment complete!"
