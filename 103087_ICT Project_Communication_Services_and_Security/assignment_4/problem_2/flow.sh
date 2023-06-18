while true 
do
    sudo ping -s 133 -i 0.001064 -c 1000  -S 11.0.0.1 13.0.0.1
    sleep 1	
done
