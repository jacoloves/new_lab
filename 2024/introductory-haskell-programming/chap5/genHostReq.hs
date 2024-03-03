getRequestUrl host apikey resource id = host ++
                                        "/" ++
                                        resource ++
                                        "/" ++
                                        id ++
                                        "?token=" ++
                                        apikey
                                        
genHostRequestBuilder host = (\apikey resource id -> getRequestUrl host apikey resource id)
  
exampleUrlBuilder = genHostRequestBuilder　"http://exmaple.com"

getApiRequestBuilder hostBuilder apiKey resource = (/id -> hostBuilder apiKey resource id)

myExampleUrlBuilder = genApiRequestBuilder exampleUrlBuilder "1337hAsk3ll"

exampleBuilder = getRequestUrl "http://exmaple.com" "1337hAsk3ll" "books"
