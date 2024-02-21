import boto3

client = boto3.client('cost-optimization-hub', region_name='us-east-1')
response = client.list_recommendations()
for item in response['items']:
    import pdb; pdb.set_trace()
    account_id = item['accountId']

    check_name = item['actionType']
    unique_id = f"{check_name}-{item['resourceId']}"
    print(unique_id)

    description = f'check_name: {check_name} data:{item} account_id: {account_id}'

    print(f"{check_name}")