#!/usr/bin/env bash

export PYTHONPATH=.
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

gunicorn -b "0.0.0.0:8080" --chdir federated_training wsgi:app --preload