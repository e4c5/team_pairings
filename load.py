import asyncio

async def main():
    # Create a list to store the connections.
    connections = []

    # Create a new connection for each URL in the list.
    for url in ['ws://localhost:8080', 'ws://localhost:8081']:
        connection = await asyncio.websockets.connect(url)
        connections.append(connection)

    # Send a message to each connection.
    for connection in connections:
        await connection.send('Hello, world!')

    # Receive a message from each connection.
    for connection in connections:
        message = await connection.recv()
        print(message)

asyncio.run(main())