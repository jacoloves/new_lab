import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as sqs from 'aws-cdk-lib/aws-sqs';

export class SqsStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const queue = new sqs.Queue(this, 'MyQueue2', {
      queueName: 'test-queue-cdk-2',
      maxMessageSizeBytes: 2048,
    });
    cdk.Tags.of(queue).add('name', 'test-queue-cdk-2');
  }
}
