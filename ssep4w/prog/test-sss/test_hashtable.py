# test_hashtable.py

#def test_should_always_pass():
#    assert 2 + 2 == 22, "This is just a dummy test"

# https://realpython.com/python-hash-table/



# test_hashtable.py

from hashtable import HashTable


#def test_should_create_hashtable():
#    assert HashTable() is not None


def test_should_create_hashtable():
    assert HashTable(size=100) is not None



def test_should_create_hashtable():
    assert HashTable(capacity=100) is not None

def test_should_report_capacity():
    assert len(HashTable(capacity=100)) == 100

