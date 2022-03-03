import asyncio
import json
import logging

import websockets as websockets

import rubiks_cube_scrambler


logger = logging.getLogger("Rubik's Cube Benchmark")


def solve_scrambles(scrambles, url):
	async def solve(scramble):
		async with websockets.connect(url) as websocket:
			await websocket.send(scramble)
			data = await websocket.recv()

		if data == 'invalid':
			return 'invalid'
		else:
			return json.loads(data)

	async def gather():
		return await asyncio.gather(*map(solve, scrambles))

	return asyncio.run(gather())


if __name__ == '__main__':
	print('\n'.join(map(str, solve_scrambles(rubiks_cube_scrambler.generate_scrambles(2), 'ws://0.0.0.0:8080'))))
