#!/usr/bin/env python3

import argparse
import json

import matplotlib
import numpy as np
from matplotlib import pyplot as plt


def plot_data(data, output=None, plot=False):
	"""
	Plot dict data with solve durations and solves move count as histograms

	:param data: data from benchmark_solver
	:param output: file to safe figure in
	:param plot: whether data should be plotted
	:return:
	"""

	times = [a['time'] for a in data['results']]
	move_count = [len(a['solution'].split(' ')) for a in data['results']]

	fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
	plt.subplots_adjust(left=0.05, right=0.8)

	ax1.set_title('Solves duration')
	ax2.set_title('Solves move count')
	plt.gcf().text(0.99, 0.8, f'solves: {len(times)}\navg. time: {np.mean(times):.3f}s\nmax. time: {max(times):.3f}s', fontsize=14, horizontalalignment='right')

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

	ax2.set_xlabel('move count')
	ax2.set_ylabel('count')

	if output is not None:
		plt.savefig(output)

	if plot:
		plt.show()


def main():
	parser = argparse.ArgumentParser(description="Rubik's Cube Solver Webserver Benchmarker Analyzer")
	parser.add_argument('file', help='Path to JSON file to analyze')
	parser.add_argument('output', help='Output path of plot')

	args = parser.parse_args()

	with open(args.file) as f:
		data = json.load(f)

	plot_data(data, args.output)


if __name__ == '__main__':
	main()
