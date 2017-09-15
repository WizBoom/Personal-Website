#!/bin/bash
. env/bin/activate
gunicorn -b 127.0.0.1:15000 app:app
