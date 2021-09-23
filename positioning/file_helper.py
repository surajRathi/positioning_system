import struct

import numpy as np


class FileLoader:
    # TODO: Use context manager and pass numpy the file handle
    def __init__(self, filename, skip_rows=0, chunk_size=None, delimiter=','):
        self.filename = filename
        self.i = skip_rows
        self.chunk_size = chunk_size
        self.delimiter = delimiter

    def __iter__(self):
        if self.chunk_size is None:
            return self.load()
        else:
            return self

    def __next__(self):
        arr = np.loadtxt(self.filename, skiprows=self.i, max_rows=self.chunk_size, delimiter=self.delimiter)
        self.i += self.chunk_size
        return arr

    def load(self) -> np.array:
        if self.chunk_size is not None:
            raise Exception("Use the __iter__ and __next__ for chunked reading.")
        return np.loadtxt(self.filename, skiprows=self.i, max_rows=self.chunk_size, delimiter=self.delimiter)


def write_csv(filename: str, arr: np.array, delimiter: str = ',', header=''):
    np.savetxt(filename, arr, delimiter=delimiter, header=header)


class ChunkedWriter:
    # TODO: Make sure the right number of columns in each chunk
    def __init__(self, filename, header=None, delimiter=','):
        self.filename = filename
        self.delimiter = delimiter
        self.header = header
        self.file = None

    def __enter__(self):
        open(self.filename, 'w').close()
        self.file = open(self.filename, 'a')
        if self.header is not None:
            print(self.header, file=self.file)
        return self

    def write(self, arr):
        if self.file is None:
            raise Exception("Use the context manager interface with this object, i.e. ```with ChunkedWrite('output.csv') as cw: ```")
        np.savetxt(self.file, arr, delimiter=self.delimiter)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()


class ChunkedNPStackWriter:
    def __init__(self, filename, delimiter=','):
        self.filename = filename
        self.file = None

    def __enter__(self):
        print("Opening npstack file")
        open(self.filename, 'w').close()
        self.file = open(self.filename, 'ab')
        return self

    def write(self, arr):
        if self.file is None:
            raise Exception("Use the context manager interface with this object, i.e. ```with ChunkedNPStackWriter('output.csv') as cw: ```")
        np.save(self.file, arr)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()


class ChunkedNPStackReader:
    def __init__(self, filename, delimiter=','):
        self.filename = filename
        self.file = None

    def __enter__(self):
        print("Opening npstack file")
        self.file = open(self.filename, 'rb')
        return self

    def __iter__(self):
        return self

    def __next__(self):
        if self.file is None:
            raise Exception("Use the context manager interface with this object, i.e. ```with ChunkedNPStackReader('output.csv') as cr: ```")
        try:
            return np.load(self.file)
        except ValueError:
            raise StopIteration()

    def stream(self):
        return np.vstack([arr for arr in self])

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()


class ChunkedNPTStackWriter:
    def __init__(self, filename, delimiter=','):
        self.filename = filename
        self.file = None

    def __enter__(self):
        print("Opening npstack_t file")
        open(self.filename, 'w').close()
        self.file = open(self.filename, 'ab')
        return self

    def write(self, t, arr):
        if self.file is None:
            raise Exception("Use the context manager interface with this object, i.e. ```with ChunkedNPStackWriter('output.csv') as cw: ```")
        # print("Writing npst", t)
        self.file.write(struct.pack('<d', t))
        # print("Writing npst", arr.shape)

        np.save(self.file, arr)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()


class ChunkedNPTStackReader:
    def __init__(self, filename, delimiter=','):
        self.filename = filename
        self.file = None
        self.time_len = struct.calcsize('<d')
        self.time_unpack = struct.Struct('<d').unpack_from

    def __enter__(self):
        print("Opening npstack file")
        self.file = open(self.filename, 'rb')
        return self

    def __iter__(self):
        return self

    def __next__(self):
        if self.file is None:
            raise Exception("Use the context manager interface with this object, i.e. ```with ChunkedNPStackReader('output.csv') as cr: ```")
        try:
            t = self.time_unpack(self.file.read(self.time_len))
            arr = np.load(self.file)
            return t, arr
        except ValueError:
            raise StopIteration()
        except struct.error:
            raise StopIteration()

    def stream(self):
        return np.vstack([arr for arr in self])

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()
