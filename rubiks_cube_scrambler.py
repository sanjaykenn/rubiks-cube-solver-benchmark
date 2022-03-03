#!/usr/bin/env python3

import random

CORNERS = ['UFR', 'ULF', 'UBL', 'URB', 'DRF', 'DFL', 'DLB', 'DBR']
EDGES = ['UR', 'UF', 'UL', 'UB', 'FR', 'FL', 'BL', 'BR', 'DR', 'DF', 'DL', 'DB']

CORNER_UV_POSITIONS = [
	[8, 20, 9],
	[6, 38, 18],
	[0, 47, 36],
	[2, 11, 45],
	[29, 15, 26],
	[27, 24, 44],
	[33, 42, 53],
	[35, 51, 17]
]

EDGE_UV_POSITIONS = [
	[5, 10],
	[7, 19],
	[3, 37],
	[1, 46],
	[23, 12],
	[21, 41],
	[50, 39],
	[48, 14],
	[32, 16],
	[28, 25],
	[30, 43],
	[34, 52],
]


def has_odd_cycles(permutation):
	"""
	Checks if a permutation has an odd or an even number of cycles

	:param permutation: list where every element from 0 to len(permutation) - 1 occurs exactly once
	:return: boolean describing if number of cycles is odd
	"""

	if len(permutation) == 0:
		return False

	visited = [False] * len(permutation)
	cycles = 1
	piece = permutation[0]

	for _ in permutation:
		if visited[piece]:
			cycles += 1
			piece = next(i for i in range(len(visited)) if not visited[i])
		visited[piece] = True
		piece = permutation[piece]

	return cycles & 1 == 1


def generate_scramble(random_object=None):
	"""
	Generate a valid Rubik's cube scramble.
	Faces have the order U (up), R (right), F (front), D (down), L (left), B (back).
	Every field on a face is visited in reading order.

	:param random_object: random.Random object to use
	:return: string of UV map as described above
	"""

	random_object = random_object or random.Random()

	corner_permutation = random_object.sample(range(8), 8)
	edge_permutation = random_object.sample(range(12), 12)

	if has_odd_cycles(corner_permutation) != has_odd_cycles(edge_permutation):
		edge_permutation[:2] = edge_permutation[1::-1]

	corner_orientation = [random_object.choice(range(3)) for _ in corner_permutation]
	corner_orientation[-1] = -sum(corner_orientation[:-1]) % 3

	edge_orientation = [random_object.choice(range(2)) for _ in edge_permutation]
	edge_orientation[-1] = sum(edge_orientation[:-1]) & 1

	uv = [None for _ in range(54)]
	uv[4], uv[13], uv[22], uv[31], uv[40], uv[49] = 'U', 'R', 'F', 'D', 'L', 'B'

	for i, corner in enumerate(corner_permutation):
		faces = [CORNERS[corner][(j + corner_orientation[i]) % 3] for j in range(len(CORNERS[corner]))]

		for face, uv_position in zip(faces, CORNER_UV_POSITIONS[i]):
			uv[uv_position] = face

	for i, edge in enumerate(edge_permutation):
		faces = [EDGES[edge][(j + edge_orientation[i]) & 1] for j in range(len(EDGES[edge]))]

		for face, uv_position in zip(faces, EDGE_UV_POSITIONS[i]):
			uv[uv_position] = face

	return ''.join(uv)


def generate_scrambles(count, random_object=None):
	"""
	Generates multiple valid Rubik's cube scrambles.

	:param count: how many scrambles to generate
	:param random_object: random.Random object to use
	:return: generator of uv's as str
	"""

	return (generate_scramble(random_object) for _ in range(count))


if __name__ == '__main__':
	print(generate_scramble())
