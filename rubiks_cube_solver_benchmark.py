import asyncio
import collections
import json
import logging
import random
import time

import matplotlib.ticker
import numpy as np
import websockets
from matplotlib import pyplot as plt

import rubiks_cube_scrambler

logger = logging.getLogger("Rubik's Cube Benchmark")


def solve_scrambles(scrambles, url):
	"""
	Send multiple scrambles to solve to server.

	:param scrambles: generator of scrambles to solve
	:param url: server url
	:param callback: callback function after every solve
	:return: list of dict, each containing the solution and the time it took to find the solution
	"""

	async def solve(scramble):
		async with websockets.connect(url) as websocket:
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


def plot_data(data, output=None):
	"""
	Plot dict data with solve durations and solves move count as histograms

	:param data: data from benchmark_solver
	:param output: file to safe figure in
	:return:
	"""

	times = [a['time'] for a in data['results']]
	move_count = [len(a['solution'].split(' ')) for a in data['results']]

	fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
	plt.subplots_adjust(left=0.05, right=0.85)

	ax1.set_title('Solves duration')
	ax2.set_title('Solves move count')
	plt.gcf().text(0.99, 0.8, f'solves: {len(times)}     \n avg. time: {np.mean(times):.3f}s', fontsize=14, horizontalalignment='right')

	*_, patches = ax1.hist(
		times,
		bins=np.logspace(np.log(min(times)), np.log(max(times)), len(times) // 10, base=np.e),
		alpha=0.8
	)

	for p in patches[::2]:
		p.set_alpha(0.9)

	ax1.set_xscale('log')

	ax1.set_xlabel('time')
	ax1.set_ylabel('count')

	ax1.xaxis.set_minor_locator(matplotlib.ticker.FixedLocator([]))
	ax1.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))

	ax2.hist(move_count, rwidth=0.8, bins=np.arange(min(move_count) - 0.5, max(move_count) + 1, 1), color='orange')
	ax2.invert_xaxis()

	ax2.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(1))
	ax2.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(5))
	ax2.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(10))

	ax2.set_xlabel('move count')
	ax2.set_ylabel('count')

	if output is not None:
		plt.savefig(output)

	plt.show()


def main():
	solve_count = 100

	print()
	data = benchmark_solver(
		rubiks_cube_scrambler.generate_scrambles(solve_count, random.Random(0)),
		'ws://0.0.0.0:8080',
		lambda i, v: print(f'\x1b[1A{(i + 1) / solve_count * 100:.2f}%')
	)
	plot_data(data, 'data.png')

	with open('data.json', 'w') as f:
		json.dump(data, f)


if __name__ == '__main__':
	main()
