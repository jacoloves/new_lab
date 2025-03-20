import * as ip from 'ip';

export const cidrSubnet = (baseCidr: string, subnetBits: number, index: number): string => {
  const [baseIp, baseMask] = baseCidr.split('/');
  const newPrefix = parseInt(baseMask) + subnetBits;

  const subnetIp = ip.fromLong(ip.toLong(baseIp) + (index << (32 - newPrefix)));
  return `${subnetIp}/${newPrefix}`;
}
