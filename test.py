from multiprocessing import Process, Queue
import os, time, random


def write(q, a, b):
    print('Process to write: %s' % os.getpid())
    for value in ['a', 'b', 'c']:
        print('Put %s %d %d to queue...' % (value, a, b))
        q.put(value)
        time.sleep(random.random())

def read(q, a, b):
    print('Process to read: %s' % os.getpid())
    while True:
        value = q.get(True)
        print('Get %s %d %d from queue.' % (value, a, b))


def fun(arg):
    print(arg[0], arg[1], arg[2])

if __name__ == '__main__':
    q = Queue()
    pw = Process(target = write, args = (q, 1, 2))  #不是tuple传进去的，是位置参数
    pr = Process(target = read, args = (q, 3, 4))
    pw.start()
    pr.start()
    pw.join()
    pr.terminate()
    
    fun((1, 2, 3))



    