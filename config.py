
import os

# Create the .streamlit directory if it doesn't exist
if not os.path.exists(os.path.expanduser("~/.streamlit")):
    os.makedirs(os.path.expanduser("~/.streamlit"))

# Write the config.toml file with the new maxUploadSize
with open(os.path.expanduser("~/.streamlit/config.toml"), "w") as f:
    f.write("[server]\n")
    f.write("maxUploadSize = 512\n")