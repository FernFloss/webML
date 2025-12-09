from minio import Minio

client = Minio(
    "localhost:9000", 
    access_key="admin",
    secret_key="password",
    secure=False,
)

bucket = "frames"
obj = "frame_000186.jpg" 

response = client.get_object(bucket, obj)
data = response.read()
response.close()
response.release_conn()

print("bytes downloaded:", len(data))

with open("downloaded_test.jpg", "wb") as f:
    f.write(data)

print("saved as downloaded_test.jpg")
