from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
import pandas as pd
import ollama
import warnings

warnings.filterwarnings('ignore')

embed_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
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

file_names, file_contents, embeddings = embed_verilog_modules('C:\\Users\\Jasper Davidson\\Documents\\Programming\\LNIS\\RAG_implementation\\rag_grab')

# Checks the dimension of each verilog module
dimension = embeddings.shape[1]

# FAISS index that exists in that many dimensions - will check similarity between different embeddings
index = faiss.IndexFlatL2(dimension)

# Adds the verilog module embeddings to the vector space
index.add(np.array(embeddings))

def search_verilog_modules(index, query, k=5):
    query_embedding = embed_model.encode([query])
    distances, indices = index.search(np.array(query_embedding), k)
    results = []
    
    for index in indices[0]:
        results.append({
            'file_name' : file_names[index],
            'file_contents': file_contents[index]
        })
        
    return results
    
description = "Design a microfluidic circuit that will mix two fluids together then incubate the output"
retrieved_modules = search_verilog_modules(index, description)

def build_prompt(query):
    query = boilerplate + "\n\n" + query
    relevant_modules = search_verilog_modules(index, query, k=2)
    
    module_contents = "";
    for module in relevant_modules:
        module_contents += module['file_contents']
    
    prompt = query + "\n\n" + module_contents
    
    return prompt
    
def prompt_ai(prompt):
    response = ollama.generate(model=model, prompt=prompt)
    return response
    
prompt = build_prompt(description)
response = prompt_ai(prompt)

print(response['response'])

    