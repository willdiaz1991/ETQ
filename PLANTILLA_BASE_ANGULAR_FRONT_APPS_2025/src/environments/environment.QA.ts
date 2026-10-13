const allowedParentOrigins: string[] = [];
const allowedIframeHosts: string[] = [];

export const environment = {
  production: false,
  baseUrl: '',
  authenticated: '',
  api: '',
  printingApiBaseUrl: 'http://127.0.0.1:8080',
  subscriptionKey: '',
  version: '1.0.0',
  environmentName: 'QA',
  allowDevAccess: true,
  allowedParentOrigins,
  allowedIframeHosts,
};
