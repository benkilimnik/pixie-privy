/*
 * Copyright 2018- The Pixie Authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

import type * as React from 'react';

import { UserManager } from 'oidc-client';

import { FormStructure } from 'app/components';
import { Auth0Buttons } from 'app/containers/auth/auth0-buttons';
import { AUTH_CLIENT_ID, AUTH_EMAIL_PASSWORD_CONN, AUTH_URI } from 'app/containers/constants';

import { getSignupArgs, CallbackArgs, getLoginArgs } from './callback-url';

export const Auth0Client = {
  makeAuth0OIDCClient(extraQueryParams?: Record<string, any>): UserManager {
    return new UserManager({
      authority: `https://${AUTH_URI}`,
      client_id: AUTH_CLIENT_ID,
      redirect_uri: `${window.location.origin}/auth/callback`,
      extraQueryParams,
      prompt: 'login',
      scope: 'openid profile email',
      // "token" is returned and propagated as the main authorization access_token.
      // "id_token" used by oidc-client-js to verify claims, errors if missing.
      // complaining about a mismatch between repsonse claims and ID token claims.
      response_type: 'token id_token',
    });
  },

  redirectToGoogleLogin(): void {
    this.makeAuth0OIDCClient(
      {
        connection: 'google-oauth2',
      },
    ).signinRedirect({
      state: {
        redirectArgs: getLoginArgs(),
      },
    });
  },

  redirectToGoogleSignup(): void {
    this.makeAuth0OIDCClient(
      {
        connection: 'google-oauth2',
      },
    ).signinRedirect({
      state: {
        redirectArgs: getSignupArgs(),
      },
    });
  },

  redirectToEmailLogin(): void {
    this.makeAuth0OIDCClient(
      {
        connection: AUTH_EMAIL_PASSWORD_CONN,
        // Manually configured in Classic Universal Login settings.
        mode: 'login',
      },
    ).signinRedirect({
      state: {
        redirectArgs: getLoginArgs(),
      },
    });
  },

  redirectToEmailSignup(): void {
    this.makeAuth0OIDCClient(
      {
        connection: AUTH_EMAIL_PASSWORD_CONN,
        // Manually configured in Classic Universal Login settings.
        mode: 'signUp',
        // Used by New Universal Login https://auth0.com/docs/login/universal-login/new-experience#signup
        screen_hint: 'signup',
      },
    ).signinRedirect(
      // Even though we are in a signup flow, the callback shouldn't "sign up" the
      // user until verification is complete.
      {
        state: {
          redirectArgs: getLoginArgs(),
        },
      },
    );
  },

  refetchToken(): void {
    // Omitting the prompt parameter with the New Universal Login will cause this to fetch the token
    // from an existing Auth0 session if possible. https://auth0.com/docs/login/universal-login/new-experience#signup
    const client = new UserManager({
      authority: `https://${AUTH_URI}`,
      client_id: AUTH_CLIENT_ID,
      redirect_uri: `${window.location.origin}/auth/callback`,
      extraQueryParams: { connection: AUTH_EMAIL_PASSWORD_CONN },
      scope: 'openid profile email',
      response_type: 'token id_token',
    });
    client.signinRedirect({
      state: {
        redirectArgs: getLoginArgs(),
      },
    });
  },

  handleToken(): Promise<CallbackArgs> {
    return new Promise<CallbackArgs>((resolve, reject) => {
      // The callback doesn't require any settings to be created.
      // That means this implementation is agnostic to the OIDC that we connected to.
      new UserManager({}).signinRedirectCallback()
        .then((user) => {
          if (!user) {
            reject(new Error('user is undefined, please try logging in again'));
          }
          resolve({
            redirectArgs: user.state.redirectArgs,
            token: {
              accessToken: user.access_token,
              idToken: user.id_token,
            },
          });
        }).catch(reject);
    });
  },

  async getPasswordLoginFlow(): Promise<FormStructure> {
    throw new Error('Password flow not available for OIDC. Use the proper OIDC flow.');
  },

  async getResetPasswordFlow(): Promise<FormStructure> {
    throw new Error('Reset Password flow not available for OIDC. Use the proper OIDC flow.');
  },

  getLoginButtons(): React.ReactElement {
    return Auth0Buttons({
      enableEmailPassword: !!AUTH_EMAIL_PASSWORD_CONN,
      googleButtonText: 'Login with Google',
      onGoogleButtonClick: () => this.redirectToGoogleLogin(),
      emailPasswordButtonText: 'Login with Email',
      onEmailPasswordButtonClick: () => this.redirectToEmailLogin(),
    });
  },

  getSignupButtons(): React.ReactElement {
    return Auth0Buttons({
      enableEmailPassword: !!AUTH_EMAIL_PASSWORD_CONN,
      googleButtonText: 'Sign-up with Google',
      onGoogleButtonClick: () => this.redirectToGoogleSignup(),
      emailPasswordButtonText: 'Sign-up with Email',
      onEmailPasswordButtonClick: () => this.redirectToEmailSignup(),
    });
  },

  async getError(): Promise<FormStructure> {
    throw new Error('error flow not supported for Auth0');
  },

  isInvitationEnabled(): boolean {
    return false;
  },

  getInvitationComponent(): React.FC {
    return undefined;
  },
};
