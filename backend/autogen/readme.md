# Steps to start the server

## Hosting our own LLM on cloud will be costly, so an alternate to it is by running on our own system 

## Step 1:

### Install LM Studio from here https://lmstudio.ai/


## Step 2:
## Download the model Mistral-7B-Instruct-v0.1-GGUF, you can choose any option from below
### 1. LM Studio
### 2. HuggingFace
### 3. URL: https://drive.google.com/drive/folders/1W0kXeXr9mix2DaszHR8c_yyC_hp43Qd_?usp=sharing 

## Step 3:

## Place the downloaded model in the following folder if you have used 2 or 3 from the above step, ignore if used 1
### ./models/

## Step 4: 

## Select the model from the drop-down in LM Studio and then start the server.
### Server starts at http://localhost:1234/v1

### Step 4.1 (Selecting the "Mistral" Model)

![F6946E88-C782-499D-82CE-3850687B9397_1_201_a](https://github.com/deepapaikar/CodeGen/assets/37763863/68628748-7de7-48a1-a9f4-0bebedcf984d)

### Step 4.2 (Select the Server button on the left side)

![204AA563-E51B-4CA2-B7F0-BB74B4B0BA75_1_201_a](https://github.com/deepapaikar/CodeGen/assets/37763863/69239ea4-0dd4-442d-9254-7fa1b898f3ce)


### Step 4.3 (Click on "Start Server" to start the Server)

![0FC88799-B975-496E-B918-8AEA78EA598E](https://github.com/deepapaikar/CodeGen/assets/37763863/bfefd9d4-a433-4488-88c8-9d584ee3f1f3)




## Step 5:
### You should be in autogen folder and Use the command: pip install -r requirements.txt


## You can play with app.py to change the prompt and make sure you are changing the config_list
