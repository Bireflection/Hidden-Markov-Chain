- 实验环境基于docker，环境安装过程中如需添加依赖可以改动Dockerfile文件。
- 创建容器的脚本可以参考run_docker.sh这个文件，或者使用docker-compose。
- jupyter可以在容器内用run_jup.sh启动，docker-compose中已配置为启动命令。
- db和pcaps为参考的实验数据，包含了pcap文件以及标签信息的sql文件，需导入数据库，可参考load_data.sh文件。
- analyzePcaps用于处理pcap文件
- 代码experiment.py主要把数据处理成fasta格式的文件，需要在实验环境内运行。
- 分析使用[HMMER](hmmer.org)做，需下载并参考文档使用。