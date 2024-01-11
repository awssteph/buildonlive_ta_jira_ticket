from jira import JIRA
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
import logging
import json
import os

account_id= boto3.client('sts').get_caller_identity().get('Account')

ignore_check_list = ['Amazon EC2 Reserved Instance Lease Expiration', 'Amazon EC2 Reserved Instance Optimization', 'Amazon ElastiCache Reserved Node Optimization', 'Amazon OpenSearch Service Reserved Instance Optimization', 'Amazon Redshift Reserved Node Optimization', 'Amazon Relational Database Service (RDS) Reserved Instance Optimization']

def lambda_handler(event, context):
    read_ta(account_id)

def get_parameter_store(parameter_name):
    client = boto3.client('ssm')
    response = client.get_parameter(
    Name=parameter_name,
    WithDecryption=True)

    API_TOKEN = response['Parameter']['Value']
    return API_TOKEN

def jira_connection(api_token): 
    # https://jira.readthedocs.io/api.html#jira.jirashell.handle_basic_auth
    email = os.environ['EMAIL']
    #api_token = os.environ['API_TOKEN']
    server = os.environ['SERVER']
    
    jira_connection = JIRA(
        basic_auth=(email, api_token),
        server= server
    )
    return jira_connection

def list_jira_tickets(jira_connection, project_key): 
    #https://www.geeksforgeeks.org/how-to-fetch-data-from-jira-in-python/
    tickets = []
    jiraOptions = {'server': ""} 
    jira = JIRA(options=jiraOptions, basic_auth=( 
    "", "")) 
    for singleIssue in jira.search_issues(jql_str='project = BuildonLiveDemo'): 
        #print('{}:{}'.format(singleIssue.key, singleIssue.fields.summary)) 
        tickets.append(f"{singleIssue.fields.summary}")
    return tickets



def jira_ticket(jira_connection, summary, description):
    project_key = os.environ['PROJECT_KEY'] 
    issue_dict = {
        'project': {'key': project_key},
        'summary': str(summary),
        'description': str(description),
        'issuetype': {'name': 'Task'}
    } 

    new_issue = jira_connection.create_issue(fields=issue_dict)
    return new_issue

def read_ta(account_id):
    parameter_name = os.environ['PARAMETER_NAME']
    api_token = get_parameter_store(parameter_name)

    connection = jira_connection(api_token)
    project_key = os.environ['PROJECT_KEY'] 
    tickets = list_jira_tickets(jira_connection, project_key)
    
    support = boto3.client('support', 'us-east-1')
    checks = support.describe_trusted_advisor_checks(language="en")["checks"] #https://boto3.amazonaws.com/v1/documentation/api/1.26.93/reference/services/support/client/describe_trusted_advisor_checks.html

    for check in checks:
        if (check.get("category") != "cost_optimizing"): continue
        try:
            result = support.describe_trusted_advisor_check_result(checkId=check["id"], language="en")['result'] #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/support/client/describe_trusted_advisor_check_result.html
            check_name = check["name"]
            if check_name not in ignore_check_list:
                for resource in result["flaggedResources"]:
                    unique_id = f"{check_name}-{resource['resourceId']}"
                    print(unique_id)

                    if unique_id in tickets: 
                        print(f"ticket for {unique_id} exist") 
                        exit
                    else: 
                        ta_data = dict(zip(check['metadata'], resource['metadata']))
                        description = f'check_name: {check_name} data:{ta_data} account_id: {account_id}'
                        ticket = jira_ticket(connection, unique_id, description )
                        print(f"{ticket}-{check_name}")
        except Exception as e:
            print(f'{type(e)}: {e}')

lambda_handler(None, None)