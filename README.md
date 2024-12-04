# RetrievalAugmentedGeneration
This repository holds the code utilized in Amazone Web Services (AWS) Lambda to implement a web page that takes in user input as a question regarding a movie and presents a response from the Meta's LLM Llama3. 

# Project Specifications
## The Retrieval
This project is connected to a vector database in AWS Bedrock Knowledge Bases which I created by using the "Amazon Titan Embeddings G1 - Text v1.2" model to embed vectors out of PDF files of various movies taken from Wikipedia and hosted in AWS S3. The first part of the code in the file (which is run on AWS Lambda) is a function that retrieves data from the knowledge base and outputs a JSON-formatted dictionary containing the text from the PDF files relevant to the user's query. 

## The Augmentation
The second part of the code file  calls this function and parses through the output to create a simple string with the relevant information. This string is used along with the user's query to create an augmented prompt. 

## The Generation
This prompt is then used to invoke Meta's LLM Llama3 to generate a response to the user's query given the relevant context. 

# Scalability and Other Uses
The movie PDF files are simply models that show the capability of the project. PDF files of any topic can be used in this project. Thus this project can be scaled to create a webpage where users can interact with any PDF text. 
