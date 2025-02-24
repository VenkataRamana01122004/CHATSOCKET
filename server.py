import asyncio
import websockets

rooms = {}

# The correct signature for the handler
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

        # Send entry message to all clients in the room
        for client in rooms[room_code]["clients"]:
            await client.send(entry_message)

        # Send existing messages to the new client
        for message in rooms[room_code]["messages"]:
            await websocket.send(message)

        # Listen for new messages from this client
        async for message in websocket:
            full_message = f"{user_name}: {message}"
            rooms[room_code]["messages"].append(full_message)

            # Broadcast the new message to all clients in the room
            for client in rooms[room_code]["clients"]:
                await client.send(full_message)

    finally:
        # Cleanup when the client disconnects
        rooms[room_code]["clients"].remove(websocket)
        print(f"{user_name} has left the chat in room {room_code}")

        exit_message = f"{user_name} has left the chat."
        rooms[room_code]["messages"].append(exit_message)

        # Notify all remaining clients in the room about the exit
        for client in rooms[room_code]["clients"]:
            await client.send(exit_message)

        # If no more clients are in the room, delete the room
        if not rooms[room_code]["clients"]:
            del rooms[room_code]
            print(f"Room {room_code} is now empty and has been deleted.")

async def main():
    try:
        start_server = await websockets.serve(handle_client, "localhost", 2004)
        # print("WebSocket server is running on ws://localhost:2004")
        await start_server.wait_closed()
    except Exception as e:
        print(f"Error starting server: {e}")

# Run the server
if __name__ == "__main__":
    asyncio.run(main())
