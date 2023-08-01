FROM public.ecr.aws/lambda/python:3.10

# Create function directory
WORKDIR /var/task

# Install the function's dependencies using file requirements.txt
# from your project directory.

COPY requirements.txt  .
RUN  pip install --upgrade pip &&\
  pip install --no-cache-dir -r requirements.txt -t .

# Copy handler function and package it
COPY lambda/*.py .
RUN rm -r requirements.txt
RUN zip -r function.zip .
CMD [ "save_chat_history.handler" ]