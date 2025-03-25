# Use Amazon Linux base image for Lambda with Python 3.10
FROM public.ecr.aws/lambda/python:3.10

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy the rest of your application code into the container
COPY . ${LAMBDA_TASK_ROOT}

# Set the handler (filename.function_name)
CMD ["main.lambda_handler"]
