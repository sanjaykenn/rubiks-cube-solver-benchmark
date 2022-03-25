#!/usr/bin/env python3

import argparse
import asyncio
import collections
import json
import logging
import random
import time

import websockets

import rubiks_cube_scrambler
import rubiks_cube_solver_benchmark_analyzer

logger = logging.getLogger("Rubik's Cube Benchmark")


def solve_scrambles(scrambles, url):
	"""
	Send multiple scrambles to solve to server.

	:param scrambles: generator of scrambles to solve
	:param url: server url
	:return: list of dict, each containing the solution and the time it took to find the solution
	"""

	async def solve(scramble):
		async with websockets.connect(url, open_timeout=None, ping_timeout=None) as websocket:
			await websocket.send(scramble)
			data = await websocket.recv()

		if data == 'invalid':
			return 'invalid'
		else:
			return json.loads(data)

	yield from map(
		asyncio.get_event_loop().run_until_complete,
		asyncio.as_completed(list(map(solve, scrambles)))
	)


def benchmark_solver(scrambles, url, callback=None):
	"""
	Benchmark rubik's cube solver server

	:param scrambles: iterator of scrambles to solve
	:param url: server url
	:param callback: callback function after each solve
	:return: dict with total time and results, each result containing time it took to solve and solution notation as string
	"""

	callback = callback or (lambda *_: None)
	result = collections.deque()

	t = time.time()
	for i, data in enumerate(solve_scrambles(scrambles, url)):
		callback(i, data)
		result.append(data)

	return {
		'total time': time.time() - t,
		'results': list(result)
	}


def main():
	parser = argparse.ArgumentParser(description="Rubik's Cube Solver Webserver Benchmarker")
	parser.add_argument('n', type=int, help='Number of scrambles to generate')
	parser.add_argument('url', help='Websocket server url')
	parser.add_argument('output', help='Output path of JSON data')
	parser.add_argument('--seed', type=int, help='Scramble generator seed')
	parser.add_argument('--output-plot', help='Output path of plot')

	args = parser.parse_args()

	print('Solving scrambles...\n')
	data = benchmark_solver(
		rubiks_cube_scrambler.generate_scrambles(args.n, random.Random(args.seed)),
		args.url,
		lambda i, v: print(f'\x1b[1A{(i + 1) / args.n * 100:.2f}%')
	)

	with open(args.output, 'w') as f:
		json.dump(data, f)

	if args.output_plot:
		rubiks_cube_solver_benchmark_analyzer.plot_data(data, args.output_plot)


if __name__ == '__main__':
	main()
