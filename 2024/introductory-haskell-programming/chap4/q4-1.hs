compareLastNames name1 name2 = if result == EQ
                                  then compare (fst name1) (fst name2)
                                  else result
  where result = compare (snd name1) (snd name2)
