#### How to setup virtual environment

##### For Linux

Run the following commands in order
1. `virtualenv env`
2. `source env/bin/activate`

##### For Windows
1. `virtualenv env`
2. `env/Scripts/activate`

If you receive an error message run the following command to gain permissions to run executable
`Set-ExecutionPolicy Unrestricted -Scope Process`

#### Handling required packages

##### Install required packages

Run the following command
1. `pip install -r requirements.txt`

##### Update requirements.txt

Run the following command
1. `pip freeze > requirements.txt`
