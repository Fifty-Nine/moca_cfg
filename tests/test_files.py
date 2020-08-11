import pytest

from moca_cfg import MoCAFiles
from textwrap import dedent

dummy_host = 'host.nowhere.local'


@pytest.fixture
def files(requests_mock):
    return MoCAFiles(dummy_host)


def test_file_map(requests_mock, files):
    requests_mock.register_uri(
        'GET',
        f'http://{dummy_host}/cmd.sh?dir',
        text=dedent("""
        0x00001234     983394 foo
        0x000F4164     204696 bar
        0x00000000          0 baz
        Found 2 files
        """)
    )

    assert files.get_file_map() == {
        'foo': {'size': 983394, 'offset': 0x11234},
        'bar': {'size': 204696, 'offset': 0x104164},
        'baz': {'size': 0, 'offset': 0x10000}
    }


def test_get_bytes(requests_mock, files):
    requests_mock.register_uri(
        'GET',
        f'http://{dummy_host}/cmd.sh?flash-dump&0x0',
        text=dedent("""
        00000000 | 4C 6F 72 65 6D 20 69 70 73 75 6D 20 64 6F 6C 6F | Lorem ipsum dolo
        00000010 | 72 20 73 69 74 20 61 6D 65 74 2C 20 63 6F 6E 73 | r sit amet, cons
        00000020 | 65 63 74 65 74 75 72 20 61 64 69 70 69 73 63 69 | ectetur adipisci
        00000030 | 6E 67 20 65 6C 69 74 2E 20 51 75 69 73 71 75 65 | ng elit. Quisque
        00000040 | 20 76 65 73 74 69 62 75 6C 75 6D 0A 66 65 6C 69 |  vestibulum.feli
        00000050 | 73 20 65 75 20 76 65 6E 65 6E 61 74 69 73 20 63 | s eu venenatis c
        00000060 | 6F 6E 73 65 63 74 65 74 75 72 2E 20 44 6F 6E 65 | onsectetur. Done
        00000070 | 63 20 76 69 74 61 65 20 72 69 73 75 73 20 65 73 | c vitae risus es
        """)
    )

    assert files.get_bytes(0) == (
        b'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque '
        b'vestibulum\nfelis eu venenatis consectetur. Donec vitae risus es'
    )


def test_get_file(requests_mock, files):
    requests_mock.register_uri(
        'GET',
        f'http://{dummy_host}/cmd.sh?dir',
        text=dedent("""
        0x00002300        362 lorem
        Found 1 file
        """)
    )
    requests_mock.register_uri(
        'GET',
        f'http://{dummy_host}/cmd.sh?flash-dump&0x12300',
        text=dedent("""
        00012300 | 4C 6F 72 65 6D 20 69 70 73 75 6D 20 64 6F 6C 6F | Lorem ipsum dolo
        00012310 | 72 20 73 69 74 20 61 6D 65 74 2C 20 63 6F 6E 73 | r sit amet, cons
        00012320 | 65 63 74 65 74 75 72 20 61 64 69 70 69 73 63 69 | ectetur adipisci
        00012330 | 6E 67 20 65 6C 69 74 2E 20 51 75 69 73 71 75 65 | ng elit. Quisque
        00012340 | 20 76 65 73 74 69 62 75 6C 75 6D 0A 66 65 6C 69 |  vestibulum.feli
        00012350 | 73 20 65 75 20 76 65 6E 65 6E 61 74 69 73 20 63 | s eu venenatis c
        00012360 | 6F 6E 73 65 63 74 65 74 75 72 2E 20 44 6F 6E 65 | onsectetur. Done
        00012370 | 63 20 76 69 74 61 65 20 72 69 73 75 73 20 65 73 | c vitae risus es
        """)
    )
    requests_mock.register_uri(
        'GET',
        f'http://{dummy_host}/cmd.sh?flash-dump&0x12380',
        text=dedent("""
        00012380 | 74 2E 20 43 72 61 73 20 61 74 20 6C 65 63 74 75 | t. Cras at lectu
        00012390 | 73 20 65 72 61 74 2E 0A 43 75 72 61 62 69 74 75 | s erat..Curabitu
        000123a0 | 72 20 73 6F 6C 6C 69 63 69 74 75 64 69 6E 20 6A | r sollicitudin j
        000123b0 | 75 73 74 6F 20 69 6E 20 74 72 69 73 74 69 71 75 | usto in tristiqu
        000123c0 | 65 20 70 6C 61 63 65 72 61 74 2E 20 4D 61 75 72 | e placerat. Maur
        000123d0 | 69 73 20 76 65 68 69 63 75 6C 61 20 6C 65 63 74 | is vehicula lect
        000123e0 | 75 73 0A 6C 65 63 74 75 73 2C 20 75 6C 74 72 69 | us.lectus, ultri
        000123f0 | 63 69 65 73 20 76 6F 6C 75 74 70 61 74 20 70 75 | cies volutpat pu
        """)
    )
    requests_mock.register_uri(
        'GET',
        f'http://{dummy_host}/cmd.sh?flash-dump&0x12400',
        text=dedent("""
        00012400 | 72 75 73 20 6D 61 6C 65 73 75 61 64 61 20 65 75 | rus malesuada eu
        00012410 | 2E 20 53 65 64 20 67 72 61 76 69 64 61 20 76 75 | . Sed gravida vu
        00012420 | 6C 70 75 74 61 74 65 20 76 65 68 69 63 75 6C 61 | lputate vehicula
        00012430 | 2E 0A 53 75 73 70 65 6E 64 69 73 73 65 20 61 6C | ..Suspendisse al
        00012440 | 69 71 75 61 6D 20 6D 61 73 73 61 20 73 69 74 20 | iquam massa sit
        00012450 | 61 6D 65 74 20 6D 69 20 66 61 75 63 69 62 75 73 | amet mi faucibus
        00012460 | 20 6D 61 78 69 6D 75 73 2E 0A FF FF FF FF FF FF |  maximus........
        00012470 | FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF | ................
        """)
    )
    assert files.get_file("lorem") == (
        b'Lorem ipsum dolor sit amet, consectetur adipiscing elit. '
        b'Quisque vestibulum\nfelis eu venenatis consectetur. Donec vitae '
        b'risus est. Cras at lectus erat.\nCurabitur sollicitudin justo '
        b'in tristique placerat. Mauris vehicula lectus\nlectus, '
        b'ultricies volutpat purus malesuada eu. Sed gravida vulputate '
        b'vehicula.\nSuspendisse aliquam massa sit amet mi faucibus '
        b'maximus.\n'
    )


def test_dump_odd_offset(requests_mock, files):
    requests_mock.register_uri(
        'GET',
        f'http://{dummy_host}/cmd.sh?flash-dump&0x7',
        text=dedent("""
        00000000 |                      07 08 09 0A 0B 0C 0D 0E 0F |        .........
        00000010 | FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF | ................
        00000020 | FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF | ................
        00000030 | FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF | ................
        00000040 | FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF | ................
        00000050 | FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF | ................
        00000060 | FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF | ................
        00000070 | FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF | ................
        """)
    )

    assert files.get_bytes(0x7) == (
        b'\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
        b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
        b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
        b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
        b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
        b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
        b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
        b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
    )


def test_dump_file_offset(requests_mock, files):
    requests_mock.register_uri(
        'GET',
        f'http://{dummy_host}/cmd.sh?dir',
        text=dedent("""
        0x00000007          9 foo
        Found 1 file
        """)
    )
    requests_mock.register_uri(
        'GET',
        f'http://{dummy_host}/cmd.sh?flash-dump&0x10007',
        text=dedent("""
        00000000 |                      AA AA AA AA AA AA AA AA AA |        .........
        00000010 | 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 | ................
        00000020 | 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 | ................
        00000030 | 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 | ................
        00000040 | 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 | ................
        00000050 | 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 | ................
        00000060 | 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 | ................
        00000070 | 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 | ................
        """)
    )

    assert files.get_file('foo') == (b'\xaa' * 9)


def test_dump_to_file(requests_mock, files):
    requests_mock.register_uri(
        'GET',
        f'http://{dummy_host}/cmd.sh?dir',
        text=dedent("""
        0x00000000          0 dummy
        Found 1 file
        """)
    )
    requests_mock.register_uri(
        'GET',
        f'http://{dummy_host}/cmd.sh?flash-dump&0x10000',
        text=dedent("""
        00000000 | FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF | ................
        00000010 | FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF | ................
        00000020 | FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF | ................
        00000030 | FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF | ................
        00000040 | FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF | ................
        00000050 | FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF | ................
        00000060 | FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF | ................
        00000070 | FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF | ................
        """)
    )

    assert files.get_file('dummy', ostream=open('/dev/null', 'bw')) is None
