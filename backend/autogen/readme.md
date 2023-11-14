# Steps to start the server

## Hosting our own LLM on cloud will be costly, so an alternate to it is by running on our own system 

## Step 1:

### Install LM Studio from here https://lmstudio.ai/


## Step 2:

## Download the model Mistral-7B-Instruct-v0.1-GGUF, you can choose any option from below
### - 1. LM Studio
### - 2. HuggingFace
### - 3. URL: https://drive.google.com/drive/folders/1W0kXeXr9mix2DaszHR8c_yyC_hp43Qd_?usp=sharing 

## Step 3:

## Place the dowloaded model in the following folder if you have used 2 or 3 from above step, ignore if used 1
### - ./models/

## Step 4: 

## Select the model from the drop down in LM Studio and then start the server.
### - Server starts at http://localhost:1234/v1


## Step 5:
### You should be in autogen folder and Use the command: pip install -r requirements.txt


## You can play with app.py to change the prompt and make sure you are changing the config_list