import os 
import json

from flask import Flask, request, Response
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from utils.response_helper import response
from repositories.UserRepository import UserRepository, User
from repositories.SessionRepository import SessionRepository
from repositories.FileRepository import FileRepository
from repositories.QueryRepository import QueryRepository
from utils.bcrypt import compare_password
from utils.jwt import sign
from middlewares.authenticate import require_authentication


app = Flask(__name__)
cors = CORS(app)

load_dotenv()

from utils.notify import sns
from utils.bucket import s3
from utils.queue import sqs
from utils.ai import load_documents, split_text, save_to_chroma, generate_rag_chain


DOC_PATH="./data/books"



@app.errorhandler(Exception)
def general_errorhandler(e):
    # message = e.description if "description" in e else str(e)
    # code = e.code if "code" in e else 500
    return response(str(e), "error", 500)

@app.route("/")
def home():
    return response("Hello world", "success", 200)


def grant_access(user: User) -> Response: 
    user_agent = request.user_agent.string
    #check if one exists
    try:
        duplicate_session = SessionRepository.find_one_by_user_id(user["id"])
        SessionRepository.remove(duplicate_session["id"])
        session = SessionRepository.create(user["id"], user_agent)
    except IndexError:
        session = SessionRepository.create(user["id"], user_agent)

    token = sign(session)
    data = {
        "userdata": {
            "id": user["id"],
            "email": user["email"],
            "created_at": user["created_at"],
        },
        "token": token
    }
    return response("Access granted", "success", 201, data)


@app.post("/access")
def gain_access():
    (email, password) = (request.json.get("email"), request.json.get("password"))
    if email == None:
        return response("Email is required", "error", 422)
    if password == None:
        return response("Password is required", "error", 422)
    try:
        user = UserRepository.find_one_by_email(email)

        #user was found
        #validate password
        if compare_password(str.encode(user["password"]), str.encode(password)):
            #at this point the password is valid so we create a session
            return grant_access(user)
        else:
            return response("Incorrect password", "error", 422)
    except IndexError:
        #at this point a user was not found so we create one
        user = UserRepository.create(email, str.encode(password))
        return grant_access(user)



@app.get("/files")
@require_authentication()
def get_files():
    #we get all the documents associated to this user
    files = FileRepository.find_all_by_user_id(request.user["id"])
    return response("Files fetched successfully", "success", 200, files)


@app.get("/file/<file_id>")
@require_authentication()
def get_file(file_id):
    try:
        file = FileRepository.find_one_by_id(file_id)
        if file["user_id"] != request.user["id"]:
            return response("User not authorized to get this file", "error", 404)
        #at this point the file belongs to the right user
        return response("File fetched successfully", "success", 200, file)
    except IndexError:
        #file not found
        return response("File not found", "error", 404)
    

@app.get("/query/<file_id>")
@require_authentication()
def get_file_queries(file_id):
    queries = QueryRepository.find_all_by_user_id_and_file_id(file_id=file_id, user_id=request.user["id"])
    return response(f"Queries for file {file_id} fetched successfully", "success", 200, queries)





@app.post("/file/upload")
@cross_origin()
@require_authentication()
def upload_document():
    doc = request.files["document"]

    #first check if the user sent a document along with this request
    if doc == None:
        return response("No file found", "error", 404)

    #then save the file to the database
    try: 
        duplicate_file = FileRepository.find_one_by_name(doc.filename)
        #check if the file is connected to the same user
        if duplicate_file["user_id"] == request.user["id"]:
            return response("Duplicate file noticed", "error", 450)
        else:
            raise IndexError("Resave this file")
    except IndexError:
        #then we save it to s3
        # s3.upload_fileobj(doc, os.getenv("AWS_BUCKET_NAME"), doc.filename)
        # url = f"https://s3.amazonaws.com/{os.getenv('AWS_BUCKET_NAME')}/{doc.filename}"
        #save it locally
        doc.save(f"{DOC_PATH}/{secure_filename(doc.filename)}")
        #then we save it to our database
        file = FileRepository.create(request.user["id"], doc.filename, url=None)
        #load
        docs = load_documents(doc.filename)
        chunks = split_text(docs)
        save_to_chroma(chunks)
        return response("Document uploaded successfully", "success", 201, file)



@app.post("/chat/<file_id>")
@cross_origin()
@require_authentication()
def chat(file_id):
    query = request.json.get("query", None)
    if query is None:
        return response("No question found", "error", 404)

    #find the file
    try:
        file = FileRepository.find_one_by_id(file_id)
    except IndexError:
        return response("File not found", "error", 404)
    
    try:
        #check for unanswered query connected to this file
        QueryRepository.find_one_unanswered_query(user_id=request.user["id"], file_id=file["id"])
        return response("Query still pending... Please wait", "error", 429)
    except IndexError:
        #at this point all queries have been answered
    
        # data = {
        #     "url": file["url"],
        #     "question": question["question"],
        #     "question_id": question["id"]
        # }

        #publish message to SQS
        # res = sqs.send_message(
        #     QueueUrl=os.getenv("AWS_QUEUE_URL"),
        #     MessageGroupId=os.getenv("SQS_MESSAGE_GROUP_ID"),
        #     MessageBody=json.dumps(data),
        #     MessageDeduplicationId=str(uuid4())
        # )
        rag = generate_rag_chain()
        res = rag.invoke(query)
        #then we register the query
        question = QueryRepository.create(question=query, file_id=file["id"], user_id=request.user["id"], answer=res) 
        # res = sns.publish(MessageBody=json.dumps(data), TopicArn=os.getenv("AWS_SNS_TOPIC_ARN"))

        return {
            "message": "Message sent to SNS",
            "status": "success",
            "data": question
        }


@app.post("/chat/complete")
@cross_origin()
def complete_chat():
    #get the SNS message details
    message_type = request.headers.get("x-amz-sns-message-type")
    sns_message = request.get_json()
    print(message_type, sns_message)
    # Confirm the subscription
    token = sns_message['Token']
    topic_arn = sns_message['TopicArn']
    sns.confirm_subscription(TopicArn=topic_arn, Token=token)

if __name__ == "__main__":
    app.run('127.0.0.1', '8000', debug=True)