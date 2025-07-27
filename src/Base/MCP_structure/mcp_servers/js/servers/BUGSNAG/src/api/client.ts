/**
 * Bugsnag API client
 */

import axios, { AxiosInstance } from 'axios';
import { ErrorCode, McpError } from '@modelcontextprotocol/sdk/types.js';

/**
 * Initialize the Bugsnag API client
 * This is done lazily when needed to allow for API key validation
 */
export function initApiClient(apiKey: string): AxiosInstance {
  if (!apiKey) {
    throw new McpError(ErrorCode.InvalidParams, 'Bugsnag API key is required');
  }

  return axios.create({
    baseURL: 'https://api.bugsnag.com',
    headers: {
      Authorization: `token ${apiKey}`,
      'X-Version': '2',
      'Content-Type': 'application/json',
    },
  });
}
