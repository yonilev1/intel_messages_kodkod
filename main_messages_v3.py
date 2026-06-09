from fastapi import FastAPI, status, HTTPException
from intel_messages_dal import IntelMessagesDAL
import logger
from pydantic import BaseModel
import mysql.connector

app = FastAPI()
my_logger = logger.get_logger('DAL')
connection = mysql.connector.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='root',
        database='soldiers_db'
    )
intel_messages_dal_instatnce = IntelMessagesDAL('127.0.0.1', 'root', 'root', 'soldiers_db', my_logger, connection)

class AddMessage(BaseModel):
    unit: str
    classification: int
    content: str
    source:str | None = None


class UpdateMessage(BaseModel):
    unit: str | None = None
    classification: int | None = None
    content: str | None = None
    source:str | None = None

app = FastAPI()


@app.get('/schema')
def get_schema():
    return intel_messages_dal_instatnce.get_schema()


@app.get('/messages')
def get_all_messages():
    return intel_messages_dal_instatnce.get_all()


@app.get('/messages/units')
def get_units():
    return intel_messages_dal_instatnce.get_distinct_units()


@app.get('/messages/{id}')
def get_message_by_id(id:int):
    message = intel_messages_dal_instatnce.get_by_id(id)
    if not message:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f'message with id {id} was not found', )
    return message


@app.post('/messages', status_code=status.HTTP_201_CREATED)
def add_message(message_details:AddMessage):
    try:
        did_add = intel_messages_dal_instatnce.create(message_details.unit, message_details.classification, message_details.content, message_details.source)
        if did_add:
            return "Message added successfully"
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to add Message to the database")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.put('/messages/{id}')
def update_message(id:int, message:UpdateMessage):
    try:
        dict_message = message.model_dump(exclude_unset=True)
        did_update =intel_messages_dal_instatnce.update(id, dict_message)
        if did_update:
            return {"message": "message updated successfully"}
        else:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f'message with id {id} was not found')
    except Exception as e:
        if isinstance(e, ValueError):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        if isinstance(e, KeyError):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.delete('/messages/{id}')
def delete_messaeg(id:int):
    try:
        did_delete =intel_messages_dal_instatnce.delete(id)
        if did_delete != 0:
            return {"message": "Message deleted successfully"}
        else:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f'message with id {id} was not found')
    except Exception as e:
        if isinstance(e, ValueError):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        if isinstance(e, KeyError):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
