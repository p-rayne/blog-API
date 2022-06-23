# blog-API
Blog backend with REST API for a test task.


## Install:
+ Clone project
+ Go to the blogAPI directory and create a .env file.
+ In the env file you need to specify the settings for django:
  > DEBUG=True  
  > SECRET_KEY=YourKey  
  > DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1]  
  > SQL_ENGINE=django.db.backends.postgresql_psycopg2  
  > SQL_DATABASE=YourDbName  
  > SQL_USER=YourUser  
  > SQL_PASSWORD=YourPassword  
  > SQL_HOST=localhost  
  > SQL_PORT=5432  


  > *Please do not forget to change the value from "Your\*" to the ones you need.*  
+ In the root directory create a virtual environment named .venv and activate it.
  > for Linux: 
  > sudo apt-get install python3-venv    *# If needed*  
  > python3 -m venv .venv  
  > source .venv/bin/activate  
+ Install dependencies
  > pip install -r requirements.txt  

Now you can run tests or view API documentation.
+ To run tests:
  > python manage.py test  
+ To see the API documentation:
  > python manage.py runsserver  
  > go to: http://127.0.0.1:8000/api/schema/swagger-ui/  

## About the project
Documentation is available at http://127.0.0.1:8000/api/schema/swagger-ui/  or in the schema.yml  
The task can be viewed in the *Task_Backend.pdf* file.
