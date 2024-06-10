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

file_names, file_contents, embeddings = embed_verilog_modules('C:\\Users\\Jasper Davidson\\Documents\\Github\\RAG\\rag_grab')

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
    
description = '''Mix 2 solutions together then incubate the output'''

def build_prompt(query):
    query = query
    relevant_modules = search_verilog_modules(index, query, 2)
    
    module_contents = "";
    for module in relevant_modules:
        module_contents += module['file_contents'] + "\n\n"
        
    prompt = boilerplate
    
    for module in relevant_modules:
        prompt += f"Module: {module['file_name']}\n{module['file_contents']}\n\n"
    
    prompt += (
        "Please generate the behavioral Verilog code for the \"experiment\" module using the provided "
        "structural modules. Ensure that the generated code is well-organized and correctly integrates the provided modules. "
        "The module should look like this:\n\n"
        "module experiment(\n"
        "    // Define your ports here\n"
        ");\n"
        "    // Integrate the provided modules here and write the necessary behavioral code\n"
        "endmodule\n\n"
        "Make sure the generated code is syntactically correct and follows the best practices of Verilog programming."
    )
    
    print(prompt)
    
    return prompt
    
def prompt_ai(prompt):
    response = ollama.generate(model=model, prompt=prompt)
    return response
    
prompt = build_prompt(description)
response = prompt_ai(prompt)

print(response['response'])