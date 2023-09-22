
Build Live Plans 
BEFORE
login terminal
export key?
open tabs
Apple-Shift-B  - close bookmarks and wordreplace


* Check Trusted advisor checks 
Show checks and explain the goal

* build code for TA
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/support/client/describe_trusted_advisor_check_result.html

* Setup board and custom field 

https://costoptimization.atlassian.net/jira/core/projects/COST/list 
Find the checks ID = 
    1. Create test ticket
    2. selecta and rightclick account id - click inspect
    3. cmf+f customf

*build code for jira
https://community.atlassian.com/t5/Jira-questions/Jira-Next-Gen-Python-API-Create-Issue-with-Custom-Field/qaq-p/2036396


* build role

* build lambda

* build layer
https://towardsdatascience.com/python-packages-in-aws-lambda-made-easy-8fbc78520e30

Create Cloud9 app
mkdir folder
cd folder
virtualenv v-env
source ./v-env/bin/activate
pip install jira
deactivate

mkdir python
cd python
cp -r ../v-env/lib64/python3.7/site-packages/* .
cd ..
zip -r jira_layer.zip python
aws lambda publish-layer-version --layer-name jira --zip-file fileb://jira_layer.zip --compatible-runtimes python3.11