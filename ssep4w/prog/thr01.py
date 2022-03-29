#!/usr/bin/env python
import argparse
import functools
import json
import os
import timeit
from queue import Queue
from threading import Thread

import requests

# How to create an API Token in Github:
# https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/
GITHUB_API_TOKEN = os.environ['GITHUB_API_TOKEN']

# can override to get the `stmt` return value
# https://hg.python.org/cpython/file/3.5/Lib/timeit.py#l70
timeit.template = """
def inner(_it, _timer{init}):
    {setup}
    _t0 = _timer()
    for _i in _it:
        retval = {stmt}
    _t1 = _timer()
    return _t1 - _t0, retval
"""


def get_username():
    """
    Returns the required "username" argument using argparse
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--username', type=str, required=True,
                        help='Github username')
    args = parser.parse_args()
    return args.username


def get_followers(username):
    """
    Returns all usernames for a Github user's followers
    """
    url = "https://api.github.com/users/{username}/followers".format(
        username=username)
    headers = {
        'Authorization': 'token {}'.format(GITHUB_API_TOKEN)
    }

    # # unauthenticated: 60 requests per hour
    # response = requests.get(url)

    # authenticated: 5000 requests per hour
    response = requests.get(url, headers=headers)

    assert response.status_code == 200
    data = json.loads(response.content.decode('utf8'))
    return [d['login'] for d in data]


def get_followers_for_queue(q, username):
    """
    Wrapper needed for `multi_threaded` to call `get_followers`
    and put the results on the Queue
    """
    for u in get_followers(username):
        # 2nd level followers
        q.put(u)


def single_threaded(username):
    """
    Returns all followers usernames using a single thread
    """
    all_usernames = {username}

    for username in get_followers(username):
        # 1st level followers
        all_usernames.add(username)
        # 2nd level followers
        all_usernames.update(get_followers(username))

    return sorted(list(all_usernames))


def multi_threaded(username):
    """
    Returns all followers usernames using multiple threads

    Uses a Queue as the data mechanism to store usernames as
    their retrieved

    Unbounded queue because we don't know how many followers
    a Github user has
    """
    q = Queue()

    q.put(username)

    threads = []

    for u in get_followers(username):
        # 1st level followers
        q.put(u)
        # 2nd level followers - get using multiple threads
        threads.append(
            Thread(target=get_followers_for_queue, args=(q, u)))

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    all_usernames = {q.get(1) for i in range(q.qsize())}
    return sorted(list(all_usernames))


def main():
    """
    Aggregates 3 levels of usernames using the Github API. The initial
    username argument, their followers, and their followers usernames

    Time both single and multi threaded implementations to
    demonstrate how I/O releases the GIL

    --username <github-username> required argument to run this script
    """
    username = get_username()

    single_time, single_usernames = timeit.timeit(
        stmt=functools.partial(single_threaded, username), number=1)

    multi_time, multi_usernames = timeit.timeit(
        stmt=functools.partial(multi_threaded, username), number=1)

    print("single_threaded time(sec):", single_time)
    print("multi_threaded time(sec):", multi_time)

    # sanity check follower count is the same
    assert len(single_usernames) == len(multi_usernames)

    print("both single_threaded and multi_threaded count: {}".format(
        len(single_usernames)))


if __name__ == '__main__':
    main()

# https://aaronlelevier.github.io/multithreading-in-python/

