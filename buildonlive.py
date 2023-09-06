from jira import JIRA
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
import logging
import json
import os

role_arn = os.environ['ROLEARN'] 
account_id= boto3.client('sts').get_caller_identity().get('Account')
account_id_jira_felid = 'customfield_10070' #os.environ['CUSTOMFELID'] 

ignore_check_list = ['Amazon EC2 Reserved Instance Lease Expiration', 'Amazon EC2 Reserved Instance Optimization', 'Amazon ElastiCache Reserved Node Optimization', 'Amazon OpenSearch Service Reserved Instance Optimization', 'Amazon Redshift Reserved Node Optimization', 'Amazon Relational Database Service (RDS) Reserved Instance Optimization']

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

def jira_ticket(jira_connection, summary, description, account_id):
    issue_dict = {
        'project': {'key': 'COST'},
        'summary': str(summary),
        'description': str(description),
        'issuetype': {'name': 'Task'},
        f'{account_id_jira_felid}': account_id # found code from inspecting the jira, must be a better way
    } 


    new_issue = jira_connection.create_issue(fields=issue_dict)

def read_ta(account_id, f_name):
    connection = jira_connection()
    f = open(f_name, "w")
    support = assume_role(account_id, "support", "us-east-1", role_arn)
    checks = support.describe_trusted_advisor_checks(language="en")["checks"]

    for check in checks:
        if (check.get("category") != "cost_optimizing"): continue
        try:
            result = support.describe_trusted_advisor_check_result(checkId=check["id"], language="en")['result']
            check_name = check["name"]
            if check_name not in ignore_check_list:
                for resource in result["flaggedResources"]:
                    print(resource)
                    jira_ticket(connection, check_name, resource['metadata'], account_id)
                
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


def get_guides(check_name):
    #tbd
    prinnt('hi')


lambda_handler(None, None)