
Build Live Plans 

* Check Trusted advisor checks 

* Setup board and custom field 
Find the checks ID


* build code
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