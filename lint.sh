#!/bin/sh
autopep8 --in-place --aggressive insert_food_data.py
autopep8 --in-place --aggressive application.py
autopep8 --in-place --aggressive apps.py
autopep8 --in-place --aggressive utilities.py
autopep8 --in-place --aggressive forms.py