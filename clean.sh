#!/bin/bash

find . -name "*~" -exec rm {} \;
find . -name "*.pyc" -exec rm {} \;
find . -name "__pycache__" -exec rmdir {} \;
