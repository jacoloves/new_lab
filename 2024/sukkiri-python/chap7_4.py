import random

print("数当てゲームを始めます。３桁の数を当ててください！")

answer = list()
for _ in range(3):
    number = random.randint(0, 9)
    answer.append(number) 

is_con = True

while is_con == True:
    prediction = list()
    for n in range(3):
        data = int(input(f'{n + 1}桁目の予想入力（0~9） >> '))
        prediction.append(data)

    hit = 0
    blow = 0
    for n in range(3):
        if prediction[n] == answer[n]:
            hit += 1
        else:
            for m in range(3):
                if prediction[n] == answer[m]:
                    blow += 1
                    break
    
    print(f'{hit}ヒット！{blow}ボール！')
    if hit == 3:
        print('正解です！')
        is_con = False
    else:
        if int(int('続けますか？ 1: 続ける 2: 終了 >> ')) == 2:
            print(f'正解は{answer}でした！')
            is_con = False
        
        