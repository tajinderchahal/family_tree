# Family Tree
This app creates a mapping of a family and contains api to find out connections related to a person

## Installation
Setup a virtual environment using below command
```
virtualenv --python=python3.7.0 <env_name>
```

After creating the virtual env, call the following commands 
```
git clone https://github.com/tajinderchahal/family_tree.git
cd family_tree
source <path/to/env_name> 
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:5000
```


## API's
Following API to get the connections belonging to a person 

Relation type choices: 
```
grand_parent
parent
children
sibling
cousin
spouse
```

```GET: /api/v1/people/<people_id>/get_connection/?relation_type=<relation_type>```
