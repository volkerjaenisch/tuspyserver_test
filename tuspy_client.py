
from tusclient import client

from data import ZeroStream

# Replace with your TUS server endpoint
tus_endpoint = 'http://localhost:8888/files/'

# Create a client for the TUS server
my_client = client.TusClient(tus_endpoint)


stream = ZeroStream(600 * 1024 * 1024)

# Upload the entire file
uploader = my_client.uploader(file_stream=stream)
uploader.upload()
