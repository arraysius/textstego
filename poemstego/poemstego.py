#!/usr/bin/python3
import argparse
from string import ascii_letters

import markovify


def get_args():
	parser = argparse.ArgumentParser(
		usage='python %(prog)s [options]',
		description='Text steganography by using Markov Chains to generate poem-like text',
		epilog='GitHub: https://github.com/cyanoise/textstego'
	)

	parser.add_argument('-x', metavar='TEXT_FILE', required=False, help='extract hidden text')
	parser.add_argument('-o', metavar='OUTPUT', required=False, help='write output to text file')
	return parser.parse_args()


def return_text(filename):
	with open(filename) as f:
		return f.read()


def generate_poem(text):
	# Build the models
	model_chicago = markovify.Text(return_text('training_text/chicago-poems.txt'))
	model_simple = markovify.Text(return_text('training_text/simplepoems.txt'))
	model_combo = markovify.combine([model_simple, model_chicago], [2, 1])

	lines = []

	for c in list(' ,.1234567890-=!@#$%^&*()_+<>?:;/\'\"\\[]{}|`~'):
		if c in text:
			text = text.replace(c, '')

	for c in text:
		while True:
			sentence = model_combo.make_short_sentence(140)

			# Ensure a sentence is generated
			if sentence is None:
				continue

			# Ensure first character is an alphabet
			if sentence[0] not in ascii_letters:
				for i in range(1, len(sentence)):
					if sentence[i] in ascii_letters:
						text = text[i:]
						break

			# Check if first letter is message letter
			if sentence[0] in (c, c.swapcase()) and sentence not in lines:
				lines.append(sentence.strip(' .-'))
				break
	return '\n'.join(lines)


def hide(output):
	# Get input from user
	message = input('Enter your message: ')
	print()

	poem = generate_poem(message)

	if output is not None:
		write_output(output, poem)
	else:
		print(poem)


def extract(filename, output):
	with open(filename, 'r') as f:
		lines = f.readlines()

	secret_message = ''.join([line[0] for line in lines])
	if output is None:
		print(secret_message)
	else:
		write_output(output, secret_message)


def write_output(filename, text):
	with open(filename, 'w') as f:
		f.write(text)


if __name__ == '__main__':
	args = get_args()

	if args.x is None:
		hide(args.o)
	else:
		extract(args.x, args.o)
