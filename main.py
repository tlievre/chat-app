from fastapi import (
    FastAPI, WebSocket, WebSocketDisconnect,
    Request, Response,
)

from Model.register_validator import RegisterValidator
from socket_manager import SocketManager
from fastapi.templating import Jinja2Templates

app = FastAPI()# manager

manager = SocketManager() # initialise socket manager

# locate templates
templates = Jinja2Templates(directory="templates")

@app.websocket("/api/chat")
async def chat(websocket: WebSocket):
    sender = websocket.cookies.get("X-Authorization")
    if sender:
        await manager.connect(websocket, sender)
        response = {
            "sender": sender,
            "message": "got connected"
        }
        await manager.broadcast(response)
        try:
            while True:
                data = await websocket.receive_json()
                await manager.broadcast(data)
        except WebSocketDisconnect:
            manager.disconnect(websocket, sender)
            response['message'] = "left"
            await manager.broadcast(response)

@app.get("/api/current_user")
def get_user(request: Request):
    return request.cookies.get("X-Authorization")

@app.post("/api/register")
def register_user(user: RegisterValidator, response: Response):
    response.set_cookie(key="X-Authorization", value=user.username, httponly=True)


@app.get("/")
def get_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/chat")
def get_chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})