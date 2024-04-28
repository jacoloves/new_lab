temp = [7.8, 9.1, 10.2, 11.0, 12.5, 12.4, 14.3, 13.8, 12.9, 12.4]

for e in temp:
    print(e)

temp_new = [7.8, 9.1, 10.2, 11.0, 12.5, "N/A", 14.3, 13.8, 12.9, 12.4] 

print(temp)
print(temp_new)

sum_tn = 0
for e in temp_new:
    if e != "N/A":
        sum_tn += e

avg = sum_tn / 9

print(avg)