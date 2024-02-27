compareLastNames name1 name2 = if lastNames1 > lastNames2
                                  then GT
                                  else if lastName1 < lastName2
                                  then LT
                                  else if firstName1 > firstName2
                                  then GT
                                  else if firstName1 < firstName2
                                  then LT
                                  else EQ
      where lastNames1 = snd name1
            lastNames2 = snd name2
            firstName1 = fst name1
            firstName2 = fst name2
