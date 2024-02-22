# 打开输入文件
with open('input.txt', 'r') as input_file:
    lines = input_file.readlines()

# 分别打开两个输出文件
with open('0.txt', 'w') as output_file_0, open('1.txt', 'w') as output_file_1:
    i = 0
    while i < len(lines):
        line = lines[i]
        # 检查每行以">"开头
        if line.startswith('>'):
            # 获取每行最后一个数字
            last_digit = line.strip().split(',')[-1]
            # 写入当前行
            if last_digit == '0':
                output_file_0.write(line)
            elif last_digit == '1':
                output_file_1.write(line)
            # 检查下一行是否存在，如果存在则一起写入
            i += 1
            while i < len(lines) and not lines[i].startswith('>'):
                if last_digit == '0':
                    output_file_0.write(lines[i])
                elif last_digit == '1':
                    output_file_1.write(lines[i])
                i += 1
        else:
            i += 1
# 完成后关闭文件
input_file.close()
output_file_0.close()
output_file_1.close()
