import os

def safe_path(file_path, c=0):
	if c == 0:
		if not os.path.isfile(file_path):
			return file_path
		else:
			c += 1
			return safe_path(file_path, c)
	else:
		path, extension = os.path.splitext(file_path)
		modified_path = path + str(c) + extension
		if not os.path.isfile(modified_path):
			return modified_path
		else:
			c += 1
			return safe_path(file_path, c)

def save(data, file_path):
	with open(safe_path(file_path), 'w') as f:
		f.write(data)
	f.close()