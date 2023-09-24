#!/bin/bash

bash gen_conf_cluster.sh
sleep 10

for i in {0..0}
do
#   for j in {0..1}
#   do
     sleep 2
     echo "$i"
     bash start_cluster.sh "$i"
#   done
done
