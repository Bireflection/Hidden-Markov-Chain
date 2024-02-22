for file in pcaps/*.pcap;
do
  # p $file > /data/pcap_txt/${file%.pcap}.txt
  filename=${file%.pcap}
  echo $filename
  argus -r $file -w - | ra -L -nn -r - -s stime dui proto saddr dir daddr sport dport bytes pkts - > logs/${filename#pcaps/}.txt  
  # argus -r $file -w - | ra -nn -r - -s stime proto saddr dir daddr sport dport bytes pkts - | awk 'BEGIN{print "number,time,SrcAddr,DstAddr,Proto,Bytes,Sport,Dport"} {print NR,$1,$2,$4,$5,$6,$7,$8,$9,$10}' > logs/${filename#pcaps/}.txt
done

