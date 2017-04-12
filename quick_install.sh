#!/bin/bash

function quit {
    echo
    echo "!!!!  $1  !!!!"
    echo
    echo "Use this script again to try another install/update of this project"
    echo
    cd ..
    rm -rf ./tmp/
    exit
}

mkdir tmp || (echo "Failed to create temporary directory in the current directory" && exit)
cd ./tmp/
git clone https://github.com/djo938/apdu_builder || quit "Failed to retrieve apdu_builder source code from github"
rm -rf ../apdu
mv ./apdu_builder/apdu ../ 
rm -rf ./*
git clone https://github.com/djo938/pytries.git || quit "Failed to retrieve pytries source code from github"
rm -rf ../tries
mv ./pytries/tries ../
rm -rf ./*
git clone https://github.com/djo938/pyshell.git || quit "Failed to retrieve supershell source code from github"
rm -rf ../pyshell
mv ./pyshell/* ../
rm ../makefile
quit "Success to install/update, use the command \`python -m pytest\` to start the shell"
