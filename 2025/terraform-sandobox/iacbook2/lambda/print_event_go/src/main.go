package main

import (
	"context"
	"encoding/json"
	"fmt"

	"github.com/aws/aws-lambda-go/lambda"
)

func HandlerRequest(ctx context.Context, event *any) error {
	jsonStr, err := json.Marshal(event)
	if err != nil {
		return err
	}

	fmt.Println(string(jsonStr))
	return nil
}

func main() {
	lambda.Start(HandlerRequest)
}
