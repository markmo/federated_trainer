federated_trainer
=================

1. Setup the scaffolding of a basic implementation of federated training

2. Added Homomorphic Encryption (`Paillier crypto system <https://en.wikipedia.org/wiki/Paillier_cryptosystem>`_)

3. Started UI components. Instead of React, using the `Svelte / Sapper framework <https://sapper.svelte.dev/>`_.
   Investigating if faster, smaller, and simpler. Svelte uses a novel approach of compiling to optimized
   Javascript instead of runtime processing of a virtual DOM as with React. In theory, this means that
   packaged code will be significantly smaller and faster. Svelte is reactive and influenced by Elm.

Differential privacy hasn't been setup yet.

.. image:: ./static/federated_training_seq_diagram.png


Requirements
------------

1. Server can't see data owner's data as its encrypted
2. Data owner can't see the model (gradient) as its also encrypted


Setup
-----

1. Install gmpy2. gmpy2 is an optimized, C-coded Python extension module that supports
   fast multiple-precision arithmetic. (Drastically improves performance.)
   ::

       brew install libmpc
       pip install gmpy2

2. Need to install the latest version of the phe (python-paillier) library to fix an
   overflow bug.
   ::

       # if already installed
       pip uninstall phe

       # cd to your source directory

       git clone https://github.com/n1analytics/python-paillier.git
       cd python-paillier
       python setup.py install


Running
-------

1. Open up 4 terminal tabs.

2. In the first tab, run:
   ::

       ./run_federated_training.sh

   This runs the server component on port 8080.

3. In the second tab, run:
   ::

       ./run_data_owner.sh

   This runs the local worker (data owner) on port 5000.

4. In the third tab, run:
   ::

       ./run_model_deployer.sh

   This runs the model deployer on port 9090.

5. In the fourth tab, run:
   ::

       curl -X POST "http://localhost:9090/model"

   This initiates model deployment. The default Linear Regression model is run in a federated fashion.

6. When the process completes, in the fourth tab, run the following to get the final cost metric
   and predicted values.
   ::

       curl "http://localhost:9090/prediction"


Notes:
------

*Why is the Paillier crypto system partially homomorphic?*

It can not do multiplication in the plaintext domain using two ciphertexts. In other words,
given :math:`E(m1)` and :math:`E(m2)`, you can not get :math:`E(m1\cdot m2)`. You can only
get :math:`E(m1+m2)`.

Given :math:`E(m1)` and :math:`m2`, you can get :math:`E(m1\cdot m2)` however. But notice
that :math:`m2` in this case was not encrypted.

*Overflow errors*

    Overflows are a consequence of the encoding scheme.

    The Paillier cryptosystem allows arithmetic over the integers modulo n. That is the numbers {0, 1, ..., n-1}.
    And thus, n-1 + 2 = 1 mod n
    or, the numbers "wrap around".

    Our encoding scheme maps floating point numbers onto the integers in such a way that it preserves arithmetic.
    We do this by encrypting the mantissa as an integer and keeping the exponent in the clear.

    However, there is a big difference to conventional floating point arithmetic.

    Whereas your computer will round to the nearest floating point number in arithmetic operations, making sure
    that the number is always representable with the available bits, our system is different. It will always
    compute the exact result. For example, if you multiply two doubles with a 53 bit mantissa each, then in our
    scheme the result will have a mantissa of 106 bits.

    The important observation here is that with every arithmetic operation, the mantissa will only grow. And as
    the mantissa is mapped onto an integer in the Paillier scheme, it will eventually be too big to be represented
    (a wrap around will occur). That's what we call an overflow.

*What type of mathematical operations can I perform?*

Once this party has received some :class:`~phe.paillier.EncryptedNumber` instances, it can perform basic
mathematical operations supported by the Paillier encryption:

* Addition of an :class:`~phe.paillier.EncryptedNumber` to a scalar
* Addition of two :class:`~phe.paillier.EncryptedNumber` instances
* Multiplication of an :class:`~phe.paillier.EncryptedNumber` by a scalar

Numpy operations that rely only on these operations are also allowed:
::

    import numpy as np
    enc_mean = np.mean(encrypted_number_list)
    enc_dot = np.dot(encrypted_number_list, [2, -400.1, 5318008])
