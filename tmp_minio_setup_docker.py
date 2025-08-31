import boto3
from botocore.client import Config
import json

print('Connecting to MinIO at http://minio:9000')

s3 = boto3.client(
    's3',
    endpoint_url='http://minio:9000',
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin',
    config=Config(signature_version='s3v4'),
)

bucket = 'media'

try:
    s3.create_bucket(Bucket=bucket)
    print('Bucket created:', bucket)
except Exception as e:
    print('Create bucket error:', type(e).__name__, e)

policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": ["s3:GetObject"],
            "Resource": [f"arn:aws:s3:::{bucket}/*"]
        }
    ]
}

try:
    s3.put_bucket_policy(Bucket=bucket, Policy=json.dumps(policy))
    print('Bucket policy set')
except Exception as e:
    print('Put policy error:', type(e).__name__, e)

# List buckets and objects for verification
try:
    print('Buckets:')
    for b in s3.list_buckets().get('Buckets', []):
        print(' -', b['Name'])
    print('Objects in bucket:')
    resp = s3.list_objects_v2(Bucket=bucket)
    for obj in resp.get('Contents', []):
        print(' -', obj['Key'])
except Exception as e:
    print('List error:', type(e).__name__, e)
