def is_leapyear(year):
    if year % 400 == 0:
        return True
    elif year % 4 == 0 and year % 100 == 0:
        return False
    elif year % 4 == 0:
        return True
    else:
        return False

input_year = int(input("西暦を入力してください >>"))

flag = is_leapyear(input_year)

if flag:
    print("西暦{}年は、閏年です".format(input_year))
else:
    print("西暦{}年は、閏年ではありません".format(input_year))