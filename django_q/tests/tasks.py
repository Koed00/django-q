import time

# simple countdown
def countdown(n):
    start_time = time.time()
    while n > 0:
        n -= 1
    stop_time = time.time()
    return stop_time - start_time


def count_letters(tup):
    total = 0
    for word in tup:
        total += len(word)
    return total

def count_letters2(obj):
    return count_letters(obj.get_words())

def result(obj):
    print('RESULT HOOK {} : {}'.format(obj.name, obj.result))


