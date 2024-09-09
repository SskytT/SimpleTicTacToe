import asyncio
import websockets
import aioconsole


async def send_message(websocket):
    try:
        while True:
            message = await aioconsole.ainput()
            await websocket.send(message)
    except websockets.ConnectionClosed:
        print("Соединение с сервером было закрыто при отправке сообщения.")
    except asyncio.CancelledError:
        print("Задача отправки сообщений была отменена.")


async def receive_message(websocket):
    try:
        while True:
            response = await websocket.recv()
            print(response)
    except websockets.ConnectionClosed:
        print("Соединение с сервером было закрыто при получении сообщения.")
    except asyncio.CancelledError:
        print("Задача получения сообщений была отменена.")


async def connect_to_server():
    try:
        async with websockets.connect("ws://localhost:8765") as websocket:
            send_task = asyncio.create_task(send_message(websocket))
            receive_task = asyncio.create_task(receive_message(websocket))

            # Ожидание завершения обеих задач
            await asyncio.gather(send_task, receive_task)
    except websockets.ConnectionClosed:
        print("Соединение с сервером было закрыто.")
    except OSError as e:
        print(f"Ошибка подключения: {e}")
    finally:
        print("Клиент отключён от сервера.")


asyncio.run(connect_to_server())
