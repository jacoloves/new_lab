addressLetter name location = locationFunction name
  where locationFunction  = getLocationFunction location

addressLetterV2 location name = flipBinaryArgs addressLetter
addressLetterNY = addressLetterV2 "ny"

flipBinaryArgs binaryFunction = (\x y -> binaryFunction y x)

subtract2 = flip (-) 2
