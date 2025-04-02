from fastapi import FastAPI, Query, Body
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl
from typing import Annotated, Literal
from datetime import datetime, time, timedelta
from uuid import UUID

app = FastAPI()  # inherits from Starlette

# Endpoints/paths - organizes concerns and resources
# http://127.0.0.1:8000/
# http://127.0.0.1:8000/docs, alternatively /redoc
# http://127.0.0.1:8000/openapi.json

# Operations/HTTP methods
# GET, POST, PUT, DELETE
# One or more can be used to communicate with any endpoint.

# Order matters: FastAPI will match the path with the first matching declared operation.
# Path operation functions are declared to be used whenever a path and operation
# matches, and then FastAPI takes care of calling the function with the correct
# parameters, extracting the data from the request. E.g. defines logic for GET
# requests to root path. So clients never call the function directly.
@app.get("/")
async def root():
    # FastAPI supports conversion of many types to JSON
    return {"message": "Hello World"}

# PATH PARAMS
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


# QUERY PARAMS - function params that are not a path param
# E.g. http://127.0.0.1:8000/items/?skip=1&limit=2 returns [{"item":"bar"},{"item":"baz"}]
# ? begins query params separated by &
# /docs shows skip and limit as query params.
# db = [{"item": "foo"}, {"item": "bar"}, {"item": "baz"}]
# @app.get("/items/")
# async def read_items(skip: int = 0, limit: int = 10):
#     return db[skip : skip + limit]

# Declare optional params by setting defaults, otherwise required.
# /docs shows item_id and short are required while q is not.
# E.g. http://127.0.0.1:8000/items/foo?short=0&q=blah return {"item_id":"foo","q":"blah","desc":"This item deserves a long description."}
# ``1``, ``True``, ``true``, ``on``, ``yes`` or any other case variation evaluates to ``True``.
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

# Query params with a Pydantic model
class FilterParams(BaseModel):
    limit: int = Field(100, gt=0, l1=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = []
@app.get("/items/")
async def read_items(filter_query: Annotated[FilterParams, Query()]):
    return filter_query


# REQUEST BODY (when path and query params are not enough) via Pydantic model.
# Sending data with POST, PUT, DELETE and request body.
# http://127.0.0.1:8000/docs#/default/create_item_items__post shows JSON schema
# for request body based on defined Pydantic model.
class Item(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: float
db = {}

# Send data via ``curl``, Postman, ``requests`` module, etc.
# curl -X 'POST' \
#   'http://127.0.0.1:8000/items/' \
#   -H 'accept: application/json' \
#   -H 'Content-Type: application/json' \
#   -d '{
#   "id": 0,
#   "name": "string",
#   "description": "string",
#   "price": 0
# }'
@app.post("/items/")
async def create_item(item: Item):
    db[item.id] = item
    return item

# Mix of path params, query params, request body.
# Function params that match path params are taken from the path
# Pydantic function params taken from request body.
# Singular type (int, float, str, bool, etc.) function params interpreted as query params.
# @app.put("/items/{item_id}")
# async def update_item(item_id: int, item: Item, q: str | None = None):
#     db[item_id] = item
#     return {"item_name": item.name, "item_id": item_id}

# Multiple request bodies
class User(BaseModel):
    username: str
    full_name: str | None = None

# Request body includes both body params as keys.
# curl -X 'POST' \
#   'http://127.0.0.1:8000/items/0' \
#   -H 'accept: application/json' \
#   -H 'Content-Type: application/json' \
#   -d '{
#   "item": {
#     "id": 0,
#     "name": "string",
#     "description": "string",
#     "price": 0
#   },
#   "user": {
#     "username": "string",
#     "full_name": "string"
#   }
# }'

@app.post("/items/{item_id}")
async def update_items(item_id: int, item: Item, user: User):
    return {"item_id": item_id, "item": item, "user": user}

# Nested request body
class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    images: list[Image] | None = None

# curl -X 'PUT' \
#   'http://127.0.0.1:8000/items/0' \
#   -H 'accept: application/json' \
#   -H 'Content-Type: application/json' \
#   -d '{
#   "name": "string",
#   "description": "string",
#   "price": 0,
#   "tax": 0,
#   "tags": [],
#   "images": [
#     {
#       "url": "https://example.com/",
#       "name": "string"
#     }
#   ]
# }'
# @app.put("/items/{item_id}")
# async def update_item(item_id: int, item: Item):
#     results = {"item_id": item_id, "item": item}
#     return results



# QUERY PARAM AND STRING VALIDATIONS - in general, any data (path params, query
# params, request body) can and should be validated :).
# Use Annotated to add metadata to function params - data about data.
# http://127.0.0.1:8000/items/?q=test query ? triggers GET.
# http://127.0.0.1:8000/items/?q=reeeaaaaaaaaaallylong returns
# {"detail":[{"type":"string_too_long","loc":["query","q"],"msg":"String should
# have at most 20 characters","input":"reeeaaaaaaaaaallylong","ctx":{"max_length":20}}]}
# Similarly fastapi.Path(), Body(), Header(), Cookie(), pydantic.Field() all
# inherit from Pydantic's FieldInfo class.
# @app.get("/items/")
# async def read_items(q: Annotated[str | None, Query(min_length=1, max_length=20)] = None):
#     results = {"items": [{"item_id": "foo"}, {"item_id": "bar"}]}
#     if q:
#         results.update({"q": q})
#     return results

# List of query params
# http://localhost:8000/items/ returns {"q":["foo","bar"]}
# http://localhost:8000/items/?q=foo returns {"q":["foo"]}
# http://localhost:8000/items/?q=foo&q=bar&q=baz returns {"q":["foo","bar","baz"]}
# @app.get("/items/")
# async def read_items(q: Annotated[list[str] | None, Query()] = ["foo", "bar"]):
#     query_items = {"q": q}
#     return query_items


# Other data types
# curl -X 'PUT' \
#   'http://127.0.0.1:8000/items/19e76b92-68d4-4202-a6f4-c555d93bed3f' \
#   -H 'accept: application/json' \
#   -H 'Content-Type: application/json' \
#   -d '{
#   "start_datetime": "2024-12-17T20:16:39.684Z",
#   "end_datetime": "2024-12-17T20:16:39.684Z",
#   "process_after": "P3D",
#   "repeat_at": "20:16:39.684Z"
# }'
@app.put("/items/{item_id}")
async def read_items(
    item_id: UUID,
    start_datetime: Annotated[datetime, Body()],
    end_datetime: Annotated[datetime, Body()],
    process_after: Annotated[timedelta, Body()],
    repeat_at: Annotated[time | None, Body()] = None,
):
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "process_after": process_after,
        "repeat_at": repeat_at,
        "start_process": start_process,
        "duration": duration,
    }
