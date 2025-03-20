export type Stages = 'dev';

export interface Environment {
  awsAccountId: string;
  cidr: string;
  enableNatGateway: boolean;
  oneNatGatewayPerAz: boolean;
}

export const environmentProps: { [key in Stages]: Environment } = {
  'dev': {
    awsAccountId: '123456789012'
    cidr: "10.0.0.0/16",
    enableNatGateway: false,
    oneNatGatewayPerAz: false,
  }
}
