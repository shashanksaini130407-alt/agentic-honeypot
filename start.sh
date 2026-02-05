#!/bin/bash
gunicorn mock_scammer:app --bind 0.0.0.0:$PORT
