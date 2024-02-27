body sumSquare squareSum = if sumSquare > squareSum
                            then sumSquare
                            else squareSum

sumSquareOrSquareSum x y = body (x^2 + y^2) ((x+y)^2)
