count = int(input())

print("カレーを召し上がれ")

print(str(count) + "皿のカレーを食べました")

ans = input("おかわりはいかがですか？(y/n) >> ")

while ans == "y":
    count += 1
    print(str(count) + "皿のカレーを食べました")
    ans = input("おかわりはいかがですか？(y/n) >> ")

print("ごちそうさまでした")