import asyncio
import websockets
import os
import signal

rooms = {}

async def handle_client(websocket, path):
    room_code = path.strip("/")
    if not room_code:
        return

    if room_code not in rooms:
        rooms[room_code] = {"clients": set(), "messages": []}

    rooms[room_code]["clients"].add(websocket)
    print(f"New connection to room: {room_code}")

    try:
        user_name = await websocket.recv()
        print(f"{user_name} has joined the chat in room {room_code}")

        entry_message = f"{user_name} has joined the chat."
        rooms[room_code]["messages"].append(entry_message)

        for client in rooms[room_code]["clients"]:
            await client.send(entry_message)

        for message in rooms[room_code]["messages"]:
            await websocket.send(message)

        async for message in websocket:
            full_message = f"{user_name}: {message}"
            rooms[room_code]["messages"].append(full_message)

            for client in rooms[room_code]["clients"]:
                await client.send(full_message)

    finally:
        rooms[room_code]["clients"].remove(websocket)
        print(f"{user_name} has left the chat in room {room_code}")

        exit_message = f"{user_name} has left the chat."
        rooms[room_code]["messages"].append(exit_message)

        for client in rooms[room_code]["clients"]:
            await client.send(exit_message)

        if not rooms[room_code]["clients"]:
            del rooms[room_code]
            print(f"Room {room_code} is now empty and has been deleted.")

async def main():
    port = int(os.getenv("PORT", 2004))  # Use Render's PORT or default to 2004 locally
    try:
        server = await websockets.serve(handle_client, "0.0.0.0", port)
        print(f"WebSocket server is running on ws://0.0.0.0:{port}")
        
        # Handle graceful shutdown
        loop = asyncio.get_running_loop()
        stop = loop.create_future()
        loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
        
        await stop  # Wait for SIGTERM to stop the server
        server.close()
        await server.wait_closed()
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == "__main__":
    asyncio.run(main())
