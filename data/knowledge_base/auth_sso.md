# Authentication and Single Sign-On (SSO) Troubleshooting

## Common Issues & Error Codes
- **Error OAuth_401**: Expired client credentials or invalid secret.
- **SAML Assertion Failed**: IdP metadata mismatch or clock skew between IdP and Service Provider.
- **Session Timeout**: Default session duration is 8 hours. Can be overridden in Org Security Settings.

## Resolution Steps
1. Verify SAML XML certificate expiration.
2. Ensure user email matches the user principal name (UPN) in Active Directory / Okta.
3. For SCIM provisioning failures, trigger a manual sync under Organization Settings > Security.