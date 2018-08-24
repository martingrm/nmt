"""
The default tf.Print op goes to STDERR
Use the function below to direct the output to stdout or a file instead
Usage:
> x=tf.ones([1, 2])
> y=tf.zeros([1, 3])
> p = x*x
> p = tf_print(p, [x, y], "hello")
> p.eval()
hello [[ 0.  0.]]
hello [[ 1.  1.]]
"""

import tensorflow as tf
import numpy

def tf_print2stdout(op, tensors, message=None):
    def print_message(x):
        sys.stdout.write(message + " %s\n" % x)
        return x

    prints = [tf.py_func(print_message, [tensor], tensor.dtype) for tensor in tensors]
    with tf.control_dependencies(prints):
        op = tf.identity(op)
    return op

def tf_print2file(op, tensors, message=None, outputFile="./output.txt", toList=True):
    def print_message(x):
        numpy.set_printoptions(threshold=numpy.nan)
        foutput = open(outputFile, 'a')
        if (toList):
            foutput.write(message + "%s\n" % x.tolist())
        else:
            foutput.write(message + "%s\n" % x)
        foutput.close()
        return x

    prints = [tf.py_func(print_message, [tensor], tensor.dtype) for tensor in tensors]
    with tf.control_dependencies(prints):
        op = tf.identity(op)
    return op


def tf_tensor2int(op, tensors, message=None):
    str = ""
    def print_message(x):
        numpy.set_printoptions(threshold=numpy.nan)
        foutput = open(outputFile, 'a')

        str = message + "%s\n" % x
        print("############################################"+str)
        return int(str)
        #foutput.write(message + "%s\n" % x)
        #foutput.close()
        #return x

    prints = [tf.py_func(print_message, [tensor], tensor.dtype) for tensor in tensors]
    #with tf.control_dependencies(prints):
    #    op = tf.identity(op)
    #x = tensors[0]
    #str = message + "%s\n" % x
    return prints[0]


def tf_printType2file(op, tensors, message=None, outputFile="./output.txt", toList=True):
    def print_message(x):
        numpy.set_printoptions(threshold=numpy.nan)
        foutput = open(outputFile, 'a')
        if (toList):
            foutput.write(message + "  --  " + x.dtype + "%s\n" % x.tolist())
        else:
            foutput.write(message + "  --  " + x.dtype +  "%s\n" % x)
        foutput.close()
        return x

    prints = [tf.py_func(print_message, [tensor], tensor.dtype) for tensor in tensors]
    with tf.control_dependencies(prints):
        op = tf.identity(op)
    return op
