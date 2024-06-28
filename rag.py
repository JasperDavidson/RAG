from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
import ollama
import warnings
import torch

warnings.filterwarnings('ignore')

os.environ["CUDA_VISIBLE_DEVICES"]=""

embed_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
model = 'codellama'
boilerplate = open('prompt.md', 'r').read()

# Index and embed the verilog modules
def embed_verilog_modules (directory):
    # Loads the files from the directory provided (probably only one file for our purposes)
    files = os.listdir(directory)
    file_contents = []
    file_names = []
    # Iterates through the files in the directory
    for file in files:
        # Opens the file, reads the contents, and adds the contents to the file_contents list
        with open(os.path.join(directory, file), 'r') as f:
            content = f.read()
            file_contents.append(content)
            file_names.append(file)
    
    # Embeds the contents of the file - allows for relevancy search
    embeddings = embed_model.encode(file_contents)
    return file_names, file_contents, embeddings

file_names, file_contents, embeddings = embed_verilog_modules('/home/u1470577/test_ollama/RAG/rag_grab')

# Checks the dimension of each verilog module
dimension = embeddings.shape[1]

# FAISS index that exists in that many dimensions - will check similarity between different embeddings
index = faiss.IndexFlatL2(dimension)

# Adds the verilog module embeddings to the vector space
index.add(np.array(embeddings))

def search_verilog_modules(index, query, k):
    query_embedding = embed_model.encode([query])
    distances, indices = index.search(np.array(query_embedding), k)
    results = []
    
    for index in indices[0]:
        results.append({
            'file_name' : file_names[index],
            'file_contents': file_contents[index]
        })
        
    return results
    
description = '''Take 4 solutions as input. Mix the 4 solutions together sequentially to create the output'''

def build_prompt(query):
    query = query
    relevant_modules = search_verilog_modules(index, query, 1)
        
    prompt = boilerplate + "\n"
    
    for module in relevant_modules:
        prompt += f"Module: {module['file_name']}\n{module['file_contents']}\n\n"
        
    # prompt += "And here are some examples of correct/incorrect runs:\n"
    # prompt += open('examples.md', 'r').read()
    
    prompt += "And here is the lab you need to create (user prompt): " + query
    
    return prompt
    
def prompt_ai(prompt):
    response = ollama.generate(model=model, prompt=prompt)
    return response
    
prompt = build_prompt(description)
response = prompt_ai(prompt)

print(response['response'])

results = open('results.txt', 'a')
results.write('\nModel: ' + model + '\nPrompt: ' + description + '\n' + response['response'] + '\n')