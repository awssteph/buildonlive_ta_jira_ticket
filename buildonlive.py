from jira import JIRA
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
import logging
import json
import os

role_arn = os.environ['ROLEARN'] 
account_id= boto3.client('sts').get_caller_identity().get('Account')


def lambda_handler(event, context):
    print(event)
    f_name = "/tmp/data.json"
    read_ta(account_id, f_name)

def jira_connection():
    email = os.environ['EMAIL']
    api_token = os.environ['API_TOKEN']
    server = os.environ['SERVER']

    jira_connection = JIRA(
        basic_auth=(email, api_token),
        server= server
    )
    return jira_connection

def jira_ticket(jira_connection, summary, description):
    issue_dict = {
        'project': {'key': 'COST'},
        'summary': str(summary),
        'description': str(description),
        'issuetype': {'name': 'Task'},
    } # coloumn 


    new_issue = jira_connection.create_issue(fields=issue_dict)

def read_ta(account_id, f_name):
    connection = jira_connection()
    f = open(f_name, "w")
    support = assume_role(account_id, "support", "us-east-1", role_arn)
    checks = support.describe_trusted_advisor_checks(language="en")["checks"]

    for check in checks:
        #print(json.dumps(check))
        if (check.get("category") != "cost_optimizing"): continue
        try:
            result = support.describe_trusted_advisor_check_result(checkId=check["id"], language="en")['result']
            check_name = check["name"]
            #print(json.dumps(result))
            #dt = result['timestamp']
            #ts = datetime.strptime(dt, '%Y-%m-%dT%H:%M:%SZ').strftime('%s')
            for resource in result["flaggedResources"]:
                print(resource)
                jira_ticket(connection, check_name, resource)
                
            #    import pdb; pdb.set_trace()
            #     output = {}
            #     if "metadata" in resource:
            #         output.update(dict(zip(check["metadata"], resource["metadata"])))
            #         del resource['metadata']
            #     resource["Region"] = resource.pop("region") if "region" in resource else '-'
            #     resource["Status"] = resource.pop("status") if "status" in resource else '-'
            #     output.update({"AccountId":account_id, "AccountName":account_name, "Category": check["category"], 'DateTime': dt, 'Timestamp': ts, "CheckName": check["name"], "CheckId": check["id"]})
            #     output.update(resource)
            #     f.write(json.dumps(output, default=_json_serial) + "\n")
        except Exception as e:
            print(f'{type(e)}: {e}')



def assume_role(account_id, service, region, role):
    assumed = boto3.client('sts').assume_role(RoleArn=role, RoleSessionName='--')
    creds = assumed['Credentials']
    return boto3.client(service, region_name=region,
        aws_access_key_id=creds['AccessKeyId'],
        aws_secret_access_key=creds['SecretAccessKey'],
        aws_session_token=creds['SessionToken'],
    )

lambda_handler(None, None)