myTail [] = []
myTail (_:xs) = xs

myGCD a 0 = a
myGCD a b = myGCD b (a `mod` b)
