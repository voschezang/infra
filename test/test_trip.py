from trip import Trip


def test_list_trips():
    data = Trip()
    assert data.list() == []

    data.data = {0: 'abc'}
    assert data.list() == [0]


def test_write_trip():
    data = Trip()
    data.write('some title', '...')
    assert data.data[0] == {'title': 'some title', 'description': '...'}


def test_read_trips():
    data = Trip()
    data.data = {0: 'abc'}
    assert data.read(0) == 'abc'
