sfOffice name = if lastName < "L"
                   then nameText ++ " - PO Box 1234 - San Francisco, CA, 94111"
                   else nameText ++ " - PO Box 1010 - San Francisco, CA, 94109"
  where lastName = snd name
        nameText = (fst name) ++ " " ++ lastName

nyOffice name = nameText ++ ":PO Box 789 - NewYork,NY,10013"
  where nameText = (fst name) ++ " " ++ (snd name)

renoOffice name = name Text ++ " - PO Box 456 - Reno,NV 89523"
  where nameText = snd name
