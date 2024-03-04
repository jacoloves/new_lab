repeat n = cycle[n]

subseq start end myList = take difference (drop start myList)
  where difference = end - start

inFirstHalf val myList = val `elem` firstHalf
  where midpoint = (length myList) `div` 2
        firstHalf = take midpoint myList

