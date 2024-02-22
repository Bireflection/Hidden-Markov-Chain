for file in pcaps/*.pcap ;
do
  # p $file > /data/pcap_txt/${file%.pcap}.txt
  filename=${file%.pcap}
  tshark -T fields -E separator=, -e frame.number -e frame.time_epoch -e ip.src -e ip.dst -e _ws.col.Protocol -e _ws.col.Length -e tcp.srcport -e tcp.dstport  -r $file > logs2/${filename#pcaps/}.txt
done

