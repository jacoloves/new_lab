add3ToAll [] = []
add3ToAll (x:xs) = (3 + x):add3ToAll xs

mul3ByAll [] = []
mul3ByAll (x:xs) = (3 * x):mul3ByAll xs
