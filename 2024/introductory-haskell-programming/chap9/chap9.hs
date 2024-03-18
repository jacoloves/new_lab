add3ToAll [] = []
add3ToAll (x:xs) = (3 + x):add3ToAll xs

mul3ByAll [] = []
mul3ByAll (x:xs) = (3 * x):mul3ByAll xs

addAnA [] = []
addAnA (x:xs) = ("a " ++ x):addAnA xs

squareAll [] = []
squareAll (x:xs) = x^2:squareAll xs

myMap f [] = []
myMap f (x:xs) = (f x):myMap f xs

myFilter test [] = []
myFilter test (x:xs) = if test x
                  then x:myFilter test xs
                  else myFilter test xs

remove test [] = []
remove test (x:xs) = if test x
                 then remove test xs
                 else x:remove test xs

cocatAll xs = foldl(++) "" xs

sumOfSquares xs = foldl (+) 0 (map (^2) xs)

rcons x y = y:x
myReverse xs = foldl rcons [] xs

myFoldl f init [] = init
myFoldl f init (x:xs) = myFoldl f newlnit xs
  where newlnit = f init x

myProduct xs = foldl (*) 1 xs
