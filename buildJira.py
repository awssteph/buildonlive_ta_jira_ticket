import boto3
from jira import JIRA
import os

client = boto3.client('support')


def lambda_handler(event,context):
    checks = client.describe_trusted_advisor_checks(language="en")["checks"] #support

    for check in checks:
        if (check.get("category") != "cost_optimizing"): continue
        result = client.describe_trusted_advisor_check_result(checkId=check["id"], language="en")['result'] #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/support/client/describe_trusted_advisor_check_result.html
        check_name = check['name']
        for resource in result["flaggedResources"]:
            ta_data = dict(zip(check['metadata'], resource['metadata']))
            #print(ta_data)
        connection  =jira_connection()
        ticket = jira_ticket(connection, check_name, ta_data)


def jira_connection(): 
   # 2. Connect to Jira
    email = os.environ['EMAIL']
    api_token = os.environ['API_TOKEN']
    server = os.environ['SERVER']

    jira_connection = JIRA(
        basic_auth=(email, api_token),
        server= server
    )
    return jira_connection

def jira_ticket(jira_connection, summary, description): #, account_id, guide):
    #3. Create Tickets
    issue_dict = {
        'project': {'key': 'COST'},
        'summary': str(summary),
        'description': str(description),
        'issuetype': {'name': 'Task'} #,
    } 
    new_issue = jira_connection.create_issue(fields=issue_dict)
    return new_issue

lambda_handler(None, None)