#!/bin/bash

function quit {
    echo
    echo "!!!!  $1  !!!!"
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
git clone https://github.com/djo938/supershell.git || quit "Failed to retrieve supershell source code from github"
rm -rf ../pyshell
mv ./supershell/* ../
quit "success to install/update"
