from typing import IO

import requests

from data import ZeroStream


def upload_file_with_tusio(
        tus_url: str,
        token: str,
        job_id: int,
        file_name: str,
        mime_type,
        stream_data: IO,
        parameter_name: str = None):
    """
    Self implemented chunked file upload using TUS.io protokoll

    Parameters
    ----------
    tus_url : The base URL of the TUS.io server
    token : Authentication token fpr TUS.io server
    job_id : Metadata for the file uploaded
    file_name : Metadata for the file uploaded
    mime_type : Metadata for the file uploaded
    stream_data : The file content as stream
    parameter_name : Metadata for the file uploaded

    Returns
    -------

    Nothing

    """

    CHUNK_SIZE = 1024 * 1024 * 5 # 5 MB

    # Metadata to accompany the file uploaded. It is available in the on_upload_finished handler
    # of the tuspyserver. And will be used to e.g. register the file in the DB.
    metadata = {
            'mime_type': mime_type,
            'file_source_path': file_name,
            'job_id': str(job_id), # TUS.io metadata params have to be strings
        }

    # In case of an input file for a job we have also to set the parameter_name in the Metadata
    if parameter_name is not None:
        metadata['parameter_name'] = parameter_name

    # The request header for the TUS Location-Request
    headers = {
        "Tus-Resumable": "1.0.0",
        # This is important since the length of the stream_data, is not known beforehand
        "Upload-Defer-Length": "1",
    }
    # The authentication cookie
    cookie = {'access_token': 'bearer ' + token}

    # THe TUS Locate request return the location for the file of the tuspyserver
    resp = requests.post(tus_url, headers=headers, cookies=cookie)
    # Check if we got a location
    if resp.status_code == 201:
        upload_url = resp.headers["Location"]
        # if upload_url and not upload_url.startswith("http"):
        #     upload_url = tus_url + upload_url.lstrip("/")
    else:
        print("TUS Server does not return a file location/upload slot")

    # The chunked upload procedure
    offset = 0

    # Main loop to chunk the stream_data
    while True:
        chunk = stream_data.read(CHUNK_SIZE)
        if not chunk:
            break
        patch_headers = {
            "Tus-Resumable": "1.0.0",
            "Upload-Offset": str(offset),
            "Content-Type": "application/offset+octet-stream"
        }
        resp = requests.patch(upload_url, data=chunk, headers=patch_headers, cookies=cookie)
        if resp.status_code not in (204, 200):
            raise Exception(f"Fehler beim Hochladen: {resp.status_code}, {resp.text}")
        offset = int(resp.headers["Upload-Offset"])

    # Now all chunks are uploaded, but the tuspyserver does not know that this was the last chunk.
    # The tuspyserver realizes that the upload is finished when the cumulative size of uploaded chunks
    # reaches the Upload-length in the Location request.
    # But in the Location request we gave "Upload-Defer-Length": "1" were not capable of measuring
    # the length of the stream.
    # Now we know the length of the stream which equals "offset".
    # In a last data wise empty request we transmit the length to the tuspyserver.

    patch_headers = {
        "Tus-Resumable": "1.0.0",
        "Upload-Offset": str(offset),
        "Upload-Length": str(offset),
        "Content-Type": "application/offset+octet-stream"
    }
    _resp = requests.patch(upload_url, data=b'', headers=patch_headers, cookies=cookie)

if __name__ == "__main__":
    url = "http://localhost:8888/files"

    stream = ZeroStream(60*1024*1024)

    upload_file_with_tusio(url, '', 1, 'xxxx', 'aaa', stream, 'ooo')

