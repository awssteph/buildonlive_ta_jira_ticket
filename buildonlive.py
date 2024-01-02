from jira import JIRA
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
import logging
import json
import os
import csv

role_arn = os.environ['ROLEARN'] 
account_id= boto3.client('sts').get_caller_identity().get('Account')
account_id_jira_felid = 'customfield_10070' #os.environ['CUSTOMFELID'] #https://community.atlassian.com/t5/Jira-questions/Jira-Next-Gen-Python-API-Create-Issue-with-Custom-Field/qaq-p/2036396
guide_jira_felid = 'customfield_10071' #os.environ['CUSTOMFELID']


ignore_check_list = ['Amazon EC2 Reserved Instance Lease Expiration', 'Amazon EC2 Reserved Instance Optimization', 'Amazon ElastiCache Reserved Node Optimization', 'Amazon OpenSearch Service Reserved Instance Optimization', 'Amazon Redshift Reserved Node Optimization', 'Amazon Relational Database Service (RDS) Reserved Instance Optimization']

def lambda_handler(event, context):
    read_ta(account_id)

def jira_connection(): # https://jira.readthedocs.io/api.html#jira.jirashell.handle_basic_auth
    email = os.environ['EMAIL']
    api_token = os.environ['API_TOKEN']
    server = os.environ['SERVER']

    jira_connection = JIRA(
        basic_auth=(email, api_token),
        server= server
    )
    return jira_connection

def jira_ticket(jira_connection, summary, description, account_id, guide):
    issue_dict = {
        'project': {'key': 'COST'},
        'summary': str(summary),
        'description': str(description),
        'issuetype': {'name': 'Task'},
        f'{account_id_jira_felid}': account_id, # found code from inspecting the jira, must be a better way
        f'{guide_jira_felid}': guide
    } 


    new_issue = jira_connection.create_issue(fields=issue_dict)
    return new_issue

def read_ta(account_id):
    connection = jira_connection()
    support = assume_role(account_id, "support", "us-east-1", role_arn)
    checks = support.describe_trusted_advisor_checks(language="en")["checks"] #https://boto3.amazonaws.com/v1/documentation/api/1.26.93/reference/services/support/client/describe_trusted_advisor_checks.html

    for check in checks:
        if (check.get("category") != "cost_optimizing"): continue
        try:
            result = support.describe_trusted_advisor_check_result(checkId=check["id"], language="en")['result'] #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/support/client/describe_trusted_advisor_check_result.html
            check_name = check["name"]
            if check_name not in ignore_check_list:
                for resource in result["flaggedResources"]:
                    ta_data = dict(zip(check['metadata'], resource['metadata']))
                    ticket = jira_ticket(connection, check_name, ta_data, account_id, guide_jira_felid )
                    print(f"{ticket}-{check_name}")
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
    print('hi')


lambda_handler(None, None)

def csv_to_json(csv_file_path, json_file_path):
    data_dict = {}
    with open(csv_file_path, encoding = 'utf-8') as csv_file_handler:
        csv_reader = csv.DictReader(csv_file_handler)
        for rows in csv_reader:
            key = rows['Serial Number']
            data_dict[key] = rows
    with open(json_file_path, 'w', encoding = 'utf-8') as json_file_handler:
        #Step 4
        json_file_handler.write(json.dumps(data_dict, indent = 4))

csv_file_path = input('Enter the absolute path of the CSV file: ')
json_file_path = input('Enter the absolute path of the JSON file: ')
 
csv_to_json(csv_file_path, json_file_path)
