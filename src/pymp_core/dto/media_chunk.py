import re

class MediaChunk():
    def __init__(self, chunk, start_byte=0, end_byte=None, fileSize=None):
        self.chunk = chunk
        self.sByte = start_byte
        self.eByte = end_byte
        self.fileSize = fileSize

    def to_content_range_header(self) -> str:
        return 'bytes {0}-{1}/{2}'.format(self.sByte, self.eByte, self.fileSize)

    def load_content_range_header(self, headerValue: str):
        sByte, eByte, fileSize = MediaChunk.parse_range_header(headerValue)
        self.sByte = sByte
        self.eByte = eByte
        self.fileSize = fileSize

    @staticmethod
    def parse_range_header(headerValue: str):
        sByte, eByte, fileSize = 0, 0, 0
        if headerValue:
            match = re.search(r'(\d+)-(\d*)\/?(\d*)', headerValue)
            if match is not None:
                groups = match.groups()
                if groups[0]:
                    sByte = int(groups[0])
                if groups[1]:
                    eByte = int(groups[1])
                if groups[2]:
                    fileSize = int(groups[2])

        return sByte, eByte, fileSize