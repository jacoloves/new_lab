file = open('sample.txt', 'r')
file_w = open('sample2.txt', 'w')
for line in file:
    file_w.write(line)

file.close()
file_w.close()