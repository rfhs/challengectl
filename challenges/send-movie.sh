#!/bin/sh
FILE=$(find /home/user/sdr/movies/*.mp4 -type f | shuf -n 1)
TIME=$(shuf -i 5-59 -n 1)
avconv -ss 00:$TIME:00 -i "$FILE" -vcodec libx264 -acodec copy -s 720x576 -f mpegts -mpegts_original_network_id 1 -mpegts_transport_stream_id 1 -mpegts_service_id 1 -metadata service_provider="$1" -metadata service_name="$2" -muxrate 3732k -y /home/user/sdr/videoout &
tsrfsend /home/user/sdr/videoout $4 $3 6000 4 1/2 1/4 8 0 0
sleep 300
#echo "stopping"
killall avconv
killall tsrfsend
