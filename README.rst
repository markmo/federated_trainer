federated_trainer
=================

1. Setup the scaffolding of a basic implementation of federated training

   Encryption and differential privacy hasn't been setup yet.


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
