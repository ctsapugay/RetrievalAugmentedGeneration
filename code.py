import os
import boto3
import json
from botocore.exceptions import ClientError

boto3_session = boto3.session.Session()
bedrock_agent_runtime_client = boto3.client('bedrock-agent-runtime')

kb_id = os.environ.get("KNOWLEDGE_BASE_ID")

def retrieve(input_text, kb_id):
    # print("Retrieving information for:", input_text, "from KB:", kb_id)
    response = bedrock_agent_runtime_client.retrieve(
        knowledgeBaseId=kb_id,
        retrievalQuery={
            'text': input_text
        },
        retrievalConfiguration={
            'vectorSearchConfiguration': {
                'numberOfResults':5
            }
        }
    )
    return response

def lambda_handler(event, context):

    ### RETRIEVAL #######################################

    # check if event contains question
    if 'question' not in event:
        return {
            'statusCode': 400,
            'body': 'No Question Provided'
        }
    
    # event contains question
    # get question
    query = event['question']
    response = retrieve(query, kb_id)
    # print(response)

    # parse through retrieval results to create context string
    context = "" # initialize string to hold context
    result_list = response["retrievalResults"]
    for result in result_list:
        context +=  str(result["content"]["text"])
    # print(context)

    # create augmented prompt
    prompt = "You are a helpful AI assistant who is expert in answering questions. "
    prompt += "Your task is to answer user's questions as factually as possible. "
    prompt += "You will be given enough context with information to answer the user's questions. "
    prompt += "\nFind the context: " + context
    prompt += "\nQuestion: " + query
    prompt += "\nNow generate a detailed answer that will be helpful for the user. Return the helpful answer."
    # print(prompt)

    ######### INVOKE LLAMA 3 ###################################
    # Create a Bedrock Runtime client in the AWS Region of your choice.
    client = boto3.client("bedrock-runtime", region_name="us-east-1")

    # Set the model ID, e.g., Llama 3 70b Instruct.
    model_id = "meta.llama3-70b-instruct-v1:0"

    # test prompt
    # thank_prompt = "Write a short thank you note to my mom thanking her for fruit"

    # Embed the prompt in Llama 3's instruction format.
    formatted_prompt = f"""
    <|begin_of_text|><|start_header_id|>user<|end_header_id|>
    {prompt}
    <|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>
    """

    # Format the request payload using the model's native structure.
    native_request = {
        "prompt": formatted_prompt,
        "max_gen_len": 512,
        "temperature": 0.5,
    }

    # Convert the native request to JSON.
    request = json.dumps(native_request)

    try:
        # Invoke the model with the request.
        response = client.invoke_model(modelId=model_id, body=request)

    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        exit(1)

    # Decode the response body.
    model_response = json.loads(response["body"].read())

    # Extract and print the response text.
    response_text = model_response["generation"]
    print(response_text)

    ############################################################

    # return {
    #     'statusCode': 200, 
    #     'body': {
    #         'query': query.strip(),
    #         'answer': response
    #     }
    # }

    return {
        'statusCode': 200, 
        'body': {
            'response': response_text
        }
    }
