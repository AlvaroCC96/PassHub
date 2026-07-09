export interface LoginInitiateResponse {
  authorization_url: string;
}

export interface AccessTokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  csrf_token: string;
}
