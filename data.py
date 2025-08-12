import io

class ZeroStream(io.RawIOBase):
    def __init__(self, size):
        self.size = size      # total size in bytes
        self.pos = 0          # current read position

    def read(self, size=-1):
        if self.pos >= self.size:
            return b''  # End of file
        if size == -1 or size > self.size - self.pos:
            size = self.size - self.pos
        self.pos += size
        return b'\x00' * size

    def seek(self, offset, whence=io.SEEK_SET):
        if whence == io.SEEK_SET:
            self.pos = min(max(offset, 0), self.size)
        elif whence == io.SEEK_CUR:
            self.pos = min(max(self.pos + offset, 0), self.size)
        elif whence == io.SEEK_END:
            self.pos = min(max(self.size + offset, 0), self.size)
        return self.pos

    def tell(self):
        return self.pos

    def readable(self):
        return True

    def seekable(self):
        return True