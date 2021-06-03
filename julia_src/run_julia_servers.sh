#!/bin/bash

START=1
END=$1
echo "starting $1 julia servers ..."

for (( c=$START; c<=$END; c++ ))
do
	julia --project=/opt/julia_src http.jl &
done

wait
echo "julia servers stopped"