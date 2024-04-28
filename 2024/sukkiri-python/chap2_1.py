lang = int(input("国語の点数 >> "))
math = int(input("算数の点数 >> "))
science = int(input("理科の点数 >> "))
society = int(input("社会の点数 >> "))
eng = int(input("英語の点数 >> "))

sum_subj = lang + math + science + society + eng
avg = sum_subj / 5

print('合計： ' + str(sum_subj) + ' 平均点： ' + str(avg))