from review import Review


def test_list_reviews():
    data = Review()
    assert data.list() == []

    data.data = {0: 'abc'}
    assert data.list() == [0]


def test_write_review():
    data = Review()
    data.write(0, 'abc')
    assert data.data[0] == 'abc'


def test_read_review():
    data = Review()
    data.data = {0: 'abc'}
    assert data.read(0) == 'abc'
