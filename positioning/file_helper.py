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


def write_csv(filename: str, arr: np.array, delimiter: str = ','):
    np.savetxt(filename, arr, delimiter=delimiter)


class ChunkedWriter:
    # TODO: Make sure the write number of columns
    def __init__(self, filename, header=None, delimiter=','):
        self.filename = filename
        self.delimiter = delimiter
        self.header = header
        self.file = None

    def __enter__(self):
        print("Opening CSV Files")
        open(self.filename, 'w').close()
        self.file = open(self.filename, 'a')
        if self.header is not None:
            print(self.header, file=self.file)
        return self

    def write(self, arr):
        if self.file is None:
            raise Exception(
                "Use the context manager interface with this object, i.e. ```with ChunkedWrite('output.csv') as cw: ```")
        np.savetxt(self.file, arr, delimiter=self.delimiter)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()
