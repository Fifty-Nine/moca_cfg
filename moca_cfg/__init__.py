import io
import itertools
import re
import os

import requests


class MoCAFiles:
    """
    Top-level interface for interacting with files on a BCM6802-based MoCA
    device with an exposed command shell.
    """
    dir_re = re.compile(r'(0x[0-9a-f]+)\s+([0-9]+)\s+(.*)$', re.I | re.M)
    hex_re = re.compile(
        r'([0-9a-f]+) \|\s+(([0-9a-f]+ )*[0-9a-f]+) \| .*$',
        re.I | re.M
    )

    def __init__(self, host="192.168.144.30"):
        """Create a new instance for interacting with a particular host.

        :param str host: The remote host.
        """
        self.host = host

    def _make_url(self, *args):
        url = 'http://'
        url += self.host
        url += '/cmd.sh'

        for i, arg in enumerate(args):
            url += '?' if i == 0 else '&'
            url += arg

        return url

    def get_file_map(self):
        """Get the list of files on the remote host.

        :return: A dictionary which maps the name of the file to its
                 size and offset in the flash memory.
        """
        r = requests.get(self._make_url("dir"))
        return {
            m.group(3): {
                'size': int(m.group(2), 10),
                'offset': (int(m.group(1), 16) + 0x10000)
            }
            for m in type(self).dir_re.finditer(r.text)
        }

    def get_bytes(self, flash_addr):
        """Get some bytes from the specified address in flash memory.

        This just returns whatever the remote provides for the given memory
        address. Typically this will be between 73 and 128 bytes.

        :param int flash_addr: The address in flash memory.
        :return: The bytes returned by the remote host.
        """
        r = requests.get(self._make_url("flash-dump", hex(flash_addr)))
        return b''.join(
            bytes.fromhex(line)
            for line in itertools.chain(
                m.group(2) for m in type(self).hex_re.finditer(r.text)
            )
        )

    def get_bytes_range(self, addr, length, ostream=None, progress=None):
        """Get a range of bytes from the flash memory.

        Like get_bytes, this returns data from the remote host's flash memory.
        Unlike get_bytes, however, this returns the exact number of bytes
        requested.

        :param int addr: The address in flash memory.
        :param int length: The number of bytes to read.
        :param ostream: If specified, bytes are written to this file instead of
                        returned.
        :param progress: If specified, information about the progress of the
                         download is written to this file in a human-readable
                         format.
        :return: The bytes read from the remote host.
        """

        if progress is None:
            progress = open(os.devnull, 'w')

        if ostream is None:
            out = io.BytesIO()
        else:
            out = ostream

        remaining = length
        while remaining > 0:
            part = self.get_bytes(addr)
            stride = min(remaining, len(part))
            addr += stride
            out.write(part[:stride])
            remaining -= stride
            print(f'{remaining} bytes remaining '
                  f'({100.0*(length - remaining)/length:2.2f}%)',
                  file=progress)

        out.flush()

        return out.getvalue() if ostream is None else None

    def get_entire_contents(self, ostream=None, progress=None):
        """Get the entire contents of the 8 MB flash memory.

        Dumps the entire contents of the flash memory. Note that this
        assumes the chip is 8 MB, as is the case on the Actiontec ECB6200.
        """
        return self.get_bytes_range(0, 0x800000, ostream, progress)

    def get_file(self, name, ostream=None, progress=None):
        """Get a file from flash memory on the remote host.

        Given a filename, attempt to download the file from the remote host
        and return the result. If `ostream` is not None, data is written to
        ostream and this method returns None.

        :param str name: The name of the file on the remote host.
        :param ostream: A file-like object to which data will be written.
        :raise: KeyError when `name` does not exist.
        :return: The contents of the file, or None if `ostream` is not None, in
        which case data will be written to `ostream`.
        """
        f = self.get_file_map()[name]
        return self.get_bytes_range(f['offset'], f['size'], ostream, progress)
