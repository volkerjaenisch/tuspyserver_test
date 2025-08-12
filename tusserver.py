from fastapi import FastAPI
from tuspyserver import create_tus_router

app = FastAPI()

# Optional: handler called when an upload finishes
def on_upload_finished(file_path: str, metadata: dict):
    print("Upload complete:", file_path)
    print("Metadata:", metadata)

# Create and mount the TUS router
tus_router = create_tus_router(
    files_dir="/tmp",
    prefix="/files"
)

app.include_router(tus_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8888)

