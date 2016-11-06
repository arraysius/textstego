with open('test.txt', 'ab') as f:
	for i in range(127):
		bytechar = bytearray([i, i + 1])
		for bit in bytechar:
			for c in hex(bit)[2:].zfill(2):
				f.write(bytearray([ord(c)]))
			f.write(bytearray([0x2d]))
		f.write(bytearray([0x09, 0x2e]))

		for j in range(3):
			f.write(bytechar)
		f.write(bytearray([0x0d, 0x0a]))
