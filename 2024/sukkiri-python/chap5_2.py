def int_input(output_str):
    input_vallue = int(input("{}を入力してください >> ".format(output_str)))
    return input_vallue

def calc_payment(money, people=2):
    dnum = money / people
    pay = dnum // 100 * 100
    if dnum > pay:
        pay = int(pay + 100)

    payorg = money - pay * (people - 1)

    return (pay, payorg)

def show_payment(pay, payorg, people=2):
    print("一人あたり{}円（{}人）、漢字は{}円です".format(pay, people, payorg))

amount = int_input("支払総額")
people = int_input("参加人数")

pay, payorg = calc_payment(amount, people)

show_payment(pay, payorg, people)
