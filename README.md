This is a program I wrote that takes the contents from different verilog files describing microfluidic circuit processes (mixing two fluids together, incubating a liquid, etc.) while working at the Laboratory for Nano-Integrated Systems. This allows scientists to craft their lab-on-chips just by prompting an LLM with a description of the experiment and using an EDA to make the chip. I chose to use Ollama as it provides access to many different LLM's that are able to code in verilog given the relevant modules I provide. It does this by embedding the modules in the file into a vector space using FAISS and then embeds the query into that same vector space. It then uses knn (K nearest neighbors) to find the most relevant verilog modules to the prompt the user gave. Finally, it passes the relevant modules + some boilerplate prompt to the LLM and behavioral verilog is returned to describe the lab.