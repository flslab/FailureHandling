#!/bin/bash

bash gen_conf_cluster.sh
sleep 10

for i in {0..59}
do
#   for j in {0..1}
#   do
     sleep 10
#     echo "$i" "$j"
     bash start_cluster.sh "$i"
#   done
done
