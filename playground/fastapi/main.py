from fastapi import FastAPI
from enum import Enum

app = FastAPI()  # inherits from Starlette

# Endpoints/paths - organizes concerns and resources
# http://127.0.0.1:8000/ 
# http://127.0.0.1:8000/docs, alternatively /redoc
# http://127.0.0.1:8000/openapi.json

# Operations/HTTP methods
# GET, POST, PUT, DELETE
# One or more can be used to communicate with any endpoint.

# Order matters: FastAPI will match the path with the first matching declared operation.
# Path operation decorator: e.g. defines logic for GET requests to root path
@app.get("/")
async def root():
    # FastAPI supports conversion of many types to JSON
    return {"message": "Hello World"}  

# Path param ``item_id``'s value gets passed to the function.
# E.g. Go to http://127.0.0.1:8000/items/5, see response {"item_id": 5}
# E.g. Go to http://127.0.0.1:8000/items/foo, see response {"detail":[{"type":
# "int_parsing","loc":["path","item_id"],"msg":"Input should be a valid integer, 
# unable to parse string as an integer","input":"foo"}]}
# FastAPI provides type validation!
# @app.get("/items/{item_id}")
# async def read_item(item_id: int):
#     return {"item_id": item_id}

# Using enums for path params. Inherit string so API docs will render correctly.
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

# E.g. http://127.0.0.1:8000/models/resnet returns {"model_name":"resnet","message":"some other model"}
# Notice endpoint specifies a resource (i.e. models), while operation and function name are verbs.
# Notice /docs and /redoc shows the enum values as options :), one of the many
# niceties of the dynamically-generated documentation.
@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}
    return {"model_name": model_name, "message": "some other model"}

# Recap 
# By using standard Python type declarations, you get:
# Editor support: error checks, autocompletion, etc.
# Type conversion: path and query params gets converted to declared types
# Data validation e.g. via Pydantic validators
# API annotation and automatic documentation


# Query params - function params that are not a path param
# E.g. http://127.0.0.1:8000/items/?skip=1&limit=2 returns [{"item":"bar"},{"item":"baz"}]
# ? begins query params separated by &
# Notice /docs shows skip and limit as query params.
db = [{"item": "foo"}, {"item": "bar"}, {"item": "baz"}]
@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    return db[skip : skip + limit]

# Declare optional params by setting defaults, otherwise required.
# Notice /docs shows item_id and short are required while q is not.
# E.g. http://127.0.0.1:8000/items/foo?short=0&q=blah return {"item_id":"foo","q":"blah","desc":"This item deserves a long description."}
# 1, True, true, on, yes or any other case variation evaluates to True.
@app.get("/items/{item_id}")
async def read_item(item_id: str, short: bool, q: str | None = None):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update({"desc": "This item deserves a long description."})
    return item

# Multiple path params are identified like kwargs, order doesn't matter.
# E.g. http://127.0.0.1:8000/users/0/items/foo returns {"user_id":0,"item":"some_foo_data"}
db = {0: {"foo": "some_foo_data", "bar": "some_bar_data"}}
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(user_id: int, item_id: str):
    return {"user_id": user_id, "item": db[user_id][item_id]}


# Request body - when path and query params are not enough.