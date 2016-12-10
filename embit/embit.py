#!/usr/bin/python3
"""
Embit.py

Invisible ASCII characters

0x1C : FS (file separator)
0x1D : GS (group separator)
0x1E : RS (record separator)
0x1F : US (unit separator)

Word wrap still causes invisible characters and lines to appear in some cases

Bits representation, two bits to be encoded as a byte
0x1C -> 00
0x1D -> 01
0x1E -> 10
0x1F -> 11
"""

import argparse
import gzip

# Special bytes to represent bits 00 to 11
spec_bytes = {'00': 0x1C, '01': 0x1D, '10': 0x1E, '11': 0x1F}


def get_args():
	parser = argparse.ArgumentParser(
		usage='python %(prog)s [options]',
		description='Text steganography by writing individual bits of secret message as bytes to text file',
		epilog='GitHub: https://github.com/cyanoise/textstego'
	)

	# required argument
	required_args = parser.add_argument_group('required arguments')
	group = required_args.add_mutually_exclusive_group(required=True)
	group.add_argument('-e', metavar='TEXT_FILE',
					   help='embed data into text file, will modify specified text file if -o is absent')
	group.add_argument('-x', metavar='TEXT_FILE', help='extract hidden data from specified text file')
	group.add_argument('-r', metavar='TEXT_FILE', help='remove hidden data in specified text file')

	# optional arguments
	parser.add_argument('-f', metavar='SECRET_FILE', required=False,
						help='external secret file to hide, used with -e')
	parser.add_argument('-c', action='store_true', required=False,
						help='compress data when hiding; decompress data when extracting (gzip)')
	parser.add_argument('-o', metavar='OUTPUT', required=False, help='write to separate text file')
	return parser.parse_args()


def hide(textfile, secretfile, compress, outputfile):
	secret_bit_bytes = bytearray()
	secret_bit_bytes.append(0x20)

	# handle user input or secret file
	if secretfile is None:
		secret_data = bytearray([ord(c) for c in input('Enter your message: ')])
	else:
		secret_data = read_bytes(secretfile)

	if compress:
		precompressed_size = len(secret_data)
		secret_data = bytearray(gzip.compress(secret_data))
		print('Compressed data {}% of original size'.format(round(len(secret_data) / precompressed_size * 100, 2)))

	# convert individual bits to bytes
	for byte in secret_data:
		secret_bit_bytes += indiv_bits_to_bytes(bin(byte)[2:].zfill(8))

	if outputfile is None:
		write_out(textfile, 'a', secret_bit_bytes)
	else:
		write_out(outputfile, 'w', read_bytes(textfile) + secret_bit_bytes)


def indiv_bits_to_bytes(byte):
	b = bytearray()
	split_by = 2
	for duobits in [byte[i:i + split_by] for i in range(0, len(byte), split_by)]:
		b.append(spec_bytes[duobits])
	return b


def extract(textfile, decompress, outputfile):
	# read text file
	file_bytes = read_bytes(textfile)

	# find special bytes
	secret_bits = ''
	for byte in file_bytes:
		if byte in spec_bytes.values():
			for key in spec_bytes.keys():
				if byte == spec_bytes[key]:
					secret_bits += key
					break

	# convert secret bits into bytes
	secret_bytes = bytearray()
	for byte in [secret_bits[i:i + 8] for i in range(0, len(secret_bits), 8)]:
		secret_bytes.append(int(byte, 2))

	if decompress:
		secret_bytes = bytearray(gzip.decompress(secret_bytes))

	# print or write output
	if outputfile is None:
		print(str(secret_bytes)[12:-2])
	else:
		write_out(outputfile, 'w', secret_bytes)


def remove(textfile):
	file_bytes = read_bytes(textfile)
	new_file_bytes = bytearray()

	# remove bytes 0x1c and 0x1d
	for byte in file_bytes:
		if byte not in spec_bytes.values():
			new_file_bytes.append(byte)

	# remove trailing space
	if new_file_bytes[-1] == 0x20:
		del new_file_bytes[-1]

	# write bytes to file (overwrite)
	with open(textfile, 'wb') as f:
		f.write(new_file_bytes)


def read_bytes(filename):
	with open(filename, 'rb')as f:
		return bytearray(f.read())


def write_out(filename, write_type, message_bytes):
	with open(filename, '{}b'.format(write_type)) as f:
		f.write(message_bytes)


if __name__ == '__main__':
	args = get_args()
	if args.e is not None:
		hide(args.e, args.f, args.c, args.o)
	elif args.x is not None:
		extract(args.x, args.c, args.o)
	else:
		remove(args.r)
