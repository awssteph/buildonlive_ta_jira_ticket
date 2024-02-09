import boto3

client = boto3.client('cost-optimization-hub', region_name='us-east-1')

response = client.list_recommendations()


for item in response['items']:
    print(item)