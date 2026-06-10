#https://github.com/yonilev1/intel_messages_kodkod
from fastapi import FastAPI, status, HTTPException, Query
from intel_messages_dal import IntelMessagesDAL
import logger
from pydantic import BaseModel
import mysql.connector
from typing import Optional

app = FastAPI()
my_logger = logger.get_logger('DAL')

def get_connection():
    connection = mysql.connector.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='root',
            database='soldiers_db'
        )
    return connection

intel_messages_dal_instatnce = IntelMessagesDAL('127.0.0.1', 'root', 'root', 'soldiers_db', my_logger)

class AddMessage(BaseModel):
    unit: str
    classification: str
    content: str
    source:str | None = None


class UpdateMessage(BaseModel):
    unit: str | None = None
    classification: str | None = None
    content: str | None = None
    source:str | None = None


@app.get('/schema')
def get_schema():
    return intel_messages_dal_instatnce.get_schema(get_connection())


@app.get('/messages')
def get_all_messages(unit:Optional[str] = Query(default=None), classification:Optional[str] =  Query(default=None)):
    if unit and classification:
        return intel_messages_dal_instatnce.get_by_unit_and_classification(unit, classification, get_connection())
    
    elif unit:
        return intel_messages_dal_instatnce.get_by_unit(unit, get_connection())
    
    elif classification:
        return intel_messages_dal_instatnce.get_by_classification(classification, get_connection())
    
    else:
        return intel_messages_dal_instatnce.get_all(get_connection())


@app.get('/messages/units')
def get_units():
    return intel_messages_dal_instatnce.get_distinct_units(get_connection())


@app.get('/messages/search')
def search_by_message_content(content):
    if content == "" or content == " " or not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='content to search is missing')
    return intel_messages_dal_instatnce.search_content(content, get_connection())


@app.get('/messages/missing-source')
def get_messages_with_missing_source():
    return intel_messages_dal_instatnce.get_missing_source(get_connection())



@app.get('/messages/{message_id}')
def get_message_by_id(message_id:int):
    message = intel_messages_dal_instatnce.get_by_id(message_id, get_connection())
    if not message:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f'message with id {message_id} was not found', )
    return message


@app.post('/messages', status_code=status.HTTP_201_CREATED)
def add_message(message_details:AddMessage):
    try:
        did_add = intel_messages_dal_instatnce.create(message_details.unit, message_details.classification, message_details.content, message_details.source, get_connection())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if did_add:
        return "Message added successfully"
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to add Message to the database")


@app.put('/messages/{message_id}')
def update_message(message_id:int, message:UpdateMessage):
    try:
        dict_message = message.model_dump(exclude_unset=True)
        did_update =intel_messages_dal_instatnce.update(message_id, dict_message, get_connection())
    except Exception as e:
        if isinstance(e, ValueError):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e))
        if isinstance(e, KeyError):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    if did_update:
        return {"message": "message updated successfully"}
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f'message with id {message_id} was not found')



@app.delete('/messages/{message_id}')
def delete_messaeg(message_id:int):
    try:
        did_delete =intel_messages_dal_instatnce.delete(message_id, get_connection())
    except Exception as e:
        if isinstance(e, ValueError):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        if isinstance(e, KeyError):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    if did_delete != 0:
        return {"message": "Message deleted successfully"}
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f'message with id {message_id} was not found')
    
