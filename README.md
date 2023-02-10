# udp-simulation

The overall goal of this assignment is to implement and evaluate different protocols for
achieving end-to-end reliable data transfer at the application layer over the unreliable
datagram protocol (UDP) transport protocol. In particular, you are asked to implement
three different sliding window protocols – Stop-and-Wait, Go Back N and Selective Repeat
– at the application layer using UDP sockets in Python. Note that the stop-and-wait
protocol can be viewed as a special kind of sliding window protocol in which sender
and receiver window sizes are both equal to 1. For each of these three sliding window
protocols, you will need to implement the two protocol endpoints referred henceforth
as sender and receiver respectively; these endpoints also act as application programs.
Data communication is unidirectional, requiring transfer of a large file from the sender to
the receiver over a link as a sequence of smaller messages. The underlying link is
assumed to be symmetric in terms of bandwidth and delay characteristics.


To test your protocol implementations and study their performance in a controlled
environment, you will need to use your COMN coursework virtual machine (VM) [1].
Specifically, the sender and receiver processes for each of the three protocols will run
within the same VM and communicate with each other over a link emulated using Linux
Traffic Control (TC) [2]. For this assignment, you only need the basic functionality of TC
to emulate a link with desired characteristics in terms of bandwidth, delay and packet
loss rate.


Since the coursework VM does not include a graphical text editor, we suggest you
develop your protocol implementations outside of it in the directory/folder containing
the ‘Vagrantfile’. These files would appear under “/vagrant” within your VM, from
where you can compile and run them.
