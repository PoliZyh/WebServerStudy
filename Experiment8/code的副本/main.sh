#!/bin/bash

file_name=$1
root_name=$2

result_path='./result'


if [ ! -d "$result_path" ]; then
    mkdir -p "$result_path"
fi


awk -f ./scripts/filter_lines.awk $file_name |
awk -f ./scripts/split_objects.awk $root_name 
