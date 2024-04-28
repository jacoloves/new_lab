for i in range(1, 10):
    for j in range(1, 10):
        if i % 2 != 0:
            ans = i * j
            if ans > 50:
                break
            print(str(ans) + " ", end='')
        else:
            continue
    if i % 2 != 0:
        print()