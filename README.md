# iReporter
[![Build Status](https://travis-ci.org/engjames/challenge3.svg?branch=develop)](https://travis-ci.org/engjames/challenge3)
[![Coverage Status](https://coveralls.io/repos/github/engjames/challenge3/badge.svg?branch=develop)](https://coveralls.io/github/engjames/challenge3?branch=develop)
[![Maintainability](https://api.codeclimate.com/v1/badges/96c4d04c86b3ee3484af/maintainability)](https://codeclimate.com/github/engjames/challenge3/maintainability)

iReporter enables any/every citizen to bring any form of corruption to the notice of appropriate authorities and the general public. Users can also report on things that needs government intervention

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 

### Prerequisites for API

Things you need to install for the API to work

* Python 

### Installing
To deploy this application follow these steps;
* clone/download this project from git hub
```
 git clone https://github.com/engjames/challenge3.git
```
* Extract the project and open it in an Editor forexample Vs code ,Pycharm or any editor of your choice.
* create a python virtual environment using the following command
```
 virtualenv  env 
``` 
* In windows, navigate to scripts in the env folder where the virtual environment exists.
```
 cd env\scripts
```
*  Activate the virtual environment using the following command ;
```
activate.bat
```
* In linux, activate the virtual environment using ;
```
source bin/activate
```
* Execute the application by running a a given command
```
 python run.py
``` 
* After running that command the server will start running at http://127.0.0.1:5000/ which is the default URL

API Endpoints currently available are;

|__Http header__| __Endpoint__ | __Functionality__    | __Body__  |
|------|-------------|------------|--------------------------------|
|POST| /auth/signup | create an account | {"firstname" : "james","lastname" : "kisuule","email" : "jamesm@gmail.com",
"password" : "kisuule","isAdmin" : "true"}  |
|POST|   /interventions     | Create an intervention ​​ record    | {"title":"drug abuse","category":"redflag","comment":"There is child abuse in kigezi","location":"5,2"}                               |
|GET|  /interventions | Get all interventions |                                            |
|GET|  /interventions<incident_id> | Get a specific intervention |                                            |
|DELETE|  /interventions<incident_id> | Delete a specific intervention |                                      |
|PUT|  /interventions/<incident_id>/location | Update the location of an intervention |                       |
|PUT|  /interventions/<incident_id>/comment | Update the comment of an intervention |                         |
|PUT|  /interventions/<incident_id>/status | Update the status of an intervention |                           |
|POST| /auth/login | Log into the sysytem  |   { "email" : "jamesm@gmail.com", "password" : "kisuule"} |
|POST|   /redflags      | Create a ​red-flag​ record     | {"title":"drug abuse","category":"redflag","comment":"There is child abuse in kigezi","location":"5,2"}                               |
|GET|  /redflags     | Get all ​red-flag​ records  |                             |
|GET|  /redflags/<incident_id>    | Get a specific ​red-flag​ record    |                   |
|PUT| /redflags/<incident_id>location   |  Edit a specific ​red-flag​ record| {"location":[2, 4]}  |
|PUT| /redflags/<incident_id>status |  Admin update status of redflg records|{"status":"resolved"}  |
|DELETE| /redflags/<incident_id>   | Delete a ​red-flag​ record  |                                    |


## Testing 
Tests can be run by running by installing pytest using the command below ;
```
 pip install pytest
```
Then after installing pytest, type the command below to run the tests
```
 pytest
```
## Built With
* [Flask](http://flask.pocoo.org/docs/1.0/) - Python web framework used

## Deployment
* The app is deployed on heroku  

## Author
* Kisuule James Francis