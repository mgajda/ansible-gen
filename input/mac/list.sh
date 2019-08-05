#!/bin/bash

for i in ~/Projects/* ~/src ~/exp; do (cd $i; echo -n "$i "; git remote -v); done > Projects
ls /usr/local/Cellar > Cellar
ls /Applications/ > Applications
