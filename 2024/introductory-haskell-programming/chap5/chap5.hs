ifEven f x = if even x
  then f x
  else x

 genIfXEven x = (\f -> ifEven f x)

 getRequestUrl host apikey resource id = host ++
                                         "/" ++
                                         resource ++
                                         "/" ++
                                         id ++
                                         "?token=" ++
                                         apikey
