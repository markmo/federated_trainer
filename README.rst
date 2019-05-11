federated_trainer
=================

In this scenario, I have three parties: Data Owner (may be many), Model Owner (beneficiary of the analytics),
and Facilitator (aka Learning Server). The data used to train the model is owned by the Data
Owners. No other party can see this data, including amongst multiple data owners. Only the Model Creator
can see the model gradients. The Training Coordinator can see neither data or model gradients; their role
is to facilitate the entire system by coordinating communications.

This first simple version is using Homomorphic Encryption to hide gradients. The data doesn't move from the
data owners. Simple HTTP REST communications is being used to coordinate actions amongst the various parties.


Progress
--------

1. Setup the scaffolding of a basic implementation of federated training

2. Added Homomorphic Encryption (`Paillier crypto system <https://en.wikipedia.org/wiki/Paillier_cryptosystem>`_)

   Having a real issue with overflow (see below). When two numbers with fractional parts are multiplied,
   the mantissa grows. The Paillier crypto library is maintaining an exact result, whereas normally the
   result is rounded to the nearest floating point number that can be represented with the available bits.
   Machine learning algorithms are iterative, therefore the size of parameter values resulting from the
   arithmetic operations is growing such that when deserialized, after being serialized to send across
   HTTP, an overflow error is occurring when trying to represent the mantissa as an int.

   As a workaround, I introduced an extra communications step to update the model owner during training
   so that the parameters can be decrypted and therefore hopefully reset the representation. This approach
   seems to make only a mild improvement.

   The library authors demonstrate a machine learning `example <https://blog.n1analytics.com/distributed-machine-learning-and-partially-homomorphic-encryption-2/>`_,
   however this example does not use serialization-deserialization of the encrypted values, so doesn't appear
   to run into this same issue.

   If this library is not suitable, I could try an alternative one.

3. Started UI components. Instead of React, using the `Svelte / Sapper framework <https://sapper.svelte.dev/>`_.
   Investigating if faster, smaller, and simpler. Svelte uses a novel approach of compiling to optimized
   Javascript instead of runtime processing of a virtual DOM as with React. In theory, this means that
   packaged code will be significantly smaller and faster. Svelte is reactive and influenced by Elm.

Differential privacy hasn't been setup yet.

TODO: update the following

.. image:: ./static/federated_training_seq_diagram.png


Requirements
------------

1. Server can't see data owner's data as its encrypted
2. Data owner can't see the model (gradient) as its also encrypted


Setup
-----

1. Install gmpy2. gmpy2 is an optimized, C-coded Python extension module that supports
   fast multi-precision arithmetic. (Drastically improves performance.)
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

       curl -H "Content-Type: application/json" -X POST "localhost:9090/models" --data @model_owners/examples/model.json

   This initiates model deployment. The default Linear Regression model is run in a federated fashion.

6. When the process completes, in the fourth tab, run the following to get the final cost metric
   and predicted values.
   ::

       curl "http://localhost:9090/prediction"


Notes:
------

*Why is the Paillier crypto system partially homomorphic?*

It cannot do multiplication in the plaintext domain using two ciphertexts. In other words,
given :math:`E(m1)` and :math:`E(m2)`, you can not get :math:`E(m1\cdot m2)`. You can only
get :math:`E(m1+m2)`.

Given :math:`E(m1)` and :math:`m2`, you can get :math:`E(m1\cdot m2)` however, but notice
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

Numpy operations that rely only on these operations are also allowed, for example:
::

    import numpy as np
    enc_mean = np.mean(encrypted_number_list)
    enc_dot = np.dot(encrypted_number_list, [2, -400.1, 5318008])


Feature types:

* Numeric

  * Continuous. Observations can take any value between a certain set of real numbers.
  * Discrete. Observations can take a value based on a count from a set of distinct whole values.

* Categorical

  * Ordinal. Observations can take a value that can be logically ordered or ranked.
  * Nominal. Observations can take a value that is not able to be organized in a logical sequence.