#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { VpcStack } from '../lib/vpc-stack';
import { environmentProps, Stages } from '../lib/environment';

const stage = process.env.STAGE as Stages;
if (!stage) {
  throw new Error('STAGE is not defined');
}

const environment = environmentProps[stage];
if (!environment) {
  throw new Error(`Invalid stage: ${stage}`);
}

const app = new cdk.App();
const st = new cdk.Stage(app, stage, {
  env: {
    account: environment.awsAccountId,
    region: 'ap-northeast-1',
  },
});

new VpcStack(st, `VpcStack`, {
  stage,
  cidr: environment.cidr,
  enableNatGateway: environment.enableNatGateway,
  oneNatGatewayPerAz: environment.oneNatGatewayPerAz,
});
