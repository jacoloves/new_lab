one = {"a", "b", "c", "d", "e"}
two = {"a", "t", "c", "d", "e"}

input("enterキーを押してください")

seki = (one & two)
wa = (one | two)

per = len(seki) / len(wa) * 100

print(str(per) + " %")