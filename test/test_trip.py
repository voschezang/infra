from trip import Trip


def test_list_reviews():
    data = Trip()
    assert data.list() == []

    data.data = {0: 'abc'}
    assert data.list() == [0]


def test_write_review():
    data = Trip()
    data.write(0, 'abc')
    assert data.data[0] == 'abc'


def test_read_review():
    data = Trip()
    data.data = {0: 'abc'}
    assert data.read(0) == 'abc'
