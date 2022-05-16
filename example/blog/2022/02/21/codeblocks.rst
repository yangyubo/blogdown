tags: [coding, python]
summary: |
  We have multi-line blocks…
  …and inline code.

Code blocks and inline code
===========================

.. contents:: local

Inline code
-----------

Non turpis. Maecenas fermentum nibh in est. Pellentesque *habitant* morbi
tristique senectus et ``pickle.load`` netus et malesuada fames ac turpis
egestas.

Literal block
-------------

Faucibus. In hac habitasse platea dictumst. Vivamus a orci at nulla
tristique **condimentum**. Donec arcu quam, dictum accumsan, convallis
accumsan, cursus sit amet, ipsum. In pharetra sagittis nunc.

.. code-block:: none

    Traceback (most recent call last):
      File "<...>/example.py", line 16, in <module>
        pickle.load(read_end)
    _pickle.UnpicklingError: pickle data was truncated

Curabitur auctor metus non mauris. Nunc condimentum nisl non augue. Donec
leo urna, dignissim vitae, porttitor ut, iaculis sit amet, sem.

Syntax highlighting
-------------------

.. code-block:: python
    :caption: stream.py

    import os, pickle, threading

    thread = threading.Thread(
        target=pickle.dump,
        args=(message, write_end, -1))
    thread.start()


A diff
------

ad litora torquent per conubia nostra, per
inceptos himenaeos. Suspendisse potenti. Quisque augue metus, hendrerit
sit amet, commodo vel, scelerisque ut, ante. Praesent euismod euismod
risus. Mauris ut metus sit amet mi cursus commodo. Morbi congue mauris ac
sapien. Donec justo. Sed congue nunc vel mauris. Pellentesque vehicula
orci id libero. In hac habitasse platea dictumst. Nulla sollicitudin,
purus id elementum dictum, dolor augue hendrerit ante, vel semper metus
enim et dolor. Pellentesque molestie nunc id enim.

.. code-block:: diff

    - read_end = os.fdopen(recv_fd, 'rb', 0)
    + read_end = os.fdopen(recv_fd, 'rb')

Senectus et netus et malesuada fames ac turpis egestas. Duis ultricies
urna. Etiam enim urna, pharetra suscipit, varius et, congue quis, odio.
Donec lobortis, elit bibendum euismod faucibus, velit nibh egestas libero,
vitae pellentesque elit augue ut massa.

Nulla consequat erat at massa. Vivamus id mi. Morbi purus enim, dapibus a,
facilisis non, tincidunt at, enim. Vestibulum ante ipsum primis in
faucibus orci luctus et ultrices posuere cubilia Curae; Duis imperdiet
eleifend arcu. Cras magna ligula, consequat at, tempor non, posuere nec,
libero. Vestibulum vel ipsum. Praesent congue justo et nunc. Vestibulum
nec felis vitae nisl pharetra sollicitudin. Quisque nec arcu vel.

Line Numbers
------------

.. code-block:: python
    :linenos:

    print(1)
    print(2)
    print(2)
    print(4)
    print(5)
    print(6)
    print(7)
    print(8)
    print(9)
    print(10)
    print(11)
    print(12)
    print(12)
    print(14)
    print(15)
    print(16)
    print(17)
    print(18)
    print(19)
    print(20)
    print(21)
    print(22)
    print(22)
    print(24)
    print(25)
    print(26)
    print(27)
    print(28)
    print(29)
    print(30)
    print(31)
    print(32)
    print(32)
    print(34)
    print(35)
    print(36)
    print(37)
    print(38)
    print(39)
    print(40)
    print(41)
    print(42)
    print(42)
    print(44)
    print(45)
    print(46)
    print(47)
    print(48)
    print(49)
    print(50)
    print(51)
    print(52)
    print(52)
    print(54)
    print(55)
    print(56)
    print(57)
    print(58)
    print(59)
