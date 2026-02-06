# Code Signing Guide for MultiDesk

This guide explains how to sign the MultiDesk executable to avoid antivirus false positives.

## Option 1: Purchase a Code Signing Certificate (Recommended)

### Step 1: Choose a Certificate Authority (CA)

**Popular Options:**
- **DigiCert** - Premium, widely trusted (~$400-600/year)
- **Sectigo (formerly Comodo)** - Good value (~$200-300/year)
- **GlobalSign** - Reliable (~$300-500/year)
- **Certum** - European, good pricing (~$200-400/year)

### Step 2: Purchase the Certificate

1. Visit the CA's website
2. Choose "Code Signing Certificate" (not SSL certificate)
3. Complete the purchase and identity verification
4. You'll receive:
   - A `.pfx` file (contains both certificate and private key)
   - Or separate `.cer` and `.key` files
   - A password to protect the certificate

### Step 3: Store Certificate Securely

**For GitHub Actions:**
1. Convert certificate to base64:
   ```powershell
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("certificate.pfx"))
   ```
2. Add as GitHub Secret:
   - Go to: Settings → Secrets and variables → Actions
   - Add secret: `CODE_SIGNING_CERT` (base64 encoded .pfx)
   - Add secret: `CODE_SIGNING_PASSWORD` (certificate password)

**For Local Signing:**
- Store `.pfx` file securely (never commit to git)
- Use environment variables for password

## Option 2: Self-Signed Certificate (For Testing Only)

**Note:** Self-signed certificates will show a warning and won't help with antivirus false positives, but useful for testing the signing process.

```powershell
# Create self-signed certificate (Windows)
$cert = New-SelfSignedCertificate -Type CodeSigningCert -Subject "CN=MultiDesk" -CertStoreLocation Cert:\CurrentUser\My
$password = ConvertTo-SecureString -String "YourPassword" -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath "multidesk.pfx" -Password $password
```

## Signing the Executable

### Manual Signing (Local)

```powershell
# Sign multidesk.exe
signtool sign /f "certificate.pfx" /p "YourPassword" /t http://timestamp.digicert.com /fd SHA256 "multidesk.exe"

# Sign sciter.dll
signtool sign /f "certificate.pfx" /p "YourPassword" /t http://timestamp.digicert.com /fd SHA256 "sciter.dll"

# Verify signature
signtool verify /pa /v "multidesk.exe"
```

### Automated Signing (GitHub Actions)

The workflow has been updated to support code signing. See `.github/workflows/multidesk-windows.yml` for the signing step.

**Requirements:**
- GitHub Secrets: `CODE_SIGNING_CERT` and `CODE_SIGNING_PASSWORD`
- Windows SDK (included in GitHub Actions runners)

## Timestamping

Always use timestamping (`/t` parameter) so signatures remain valid after certificate expiration.

**Timestamp Servers:**
- DigiCert: `http://timestamp.digicert.com`
- Sectigo: `http://timestamp.sectigo.com`
- GlobalSign: `http://timestamp.globalsign.com/tsa/r6advanced1`

## Verification

After signing, verify the signature:

```powershell
# Check signature details
Get-AuthenticodeSignature "multidesk.exe"

# Verify with signtool
signtool verify /pa /v "multidesk.exe"
```

## Cost Comparison

| Option | Cost/Year | Trust Level | Antivirus Trust |
|--------|-----------|------------|-----------------|
| Self-Signed | Free | None | No benefit |
| Standard Code Signing | $200-400 | High | Good |
| EV Code Signing | $400-800 | Very High | Excellent |

## Important Notes

1. **Certificate Storage:** Never commit certificates or passwords to git
2. **Expiration:** Certificates expire annually - renew before expiration
3. **Revocation:** If private key is compromised, revoke certificate immediately
4. **Multiple Files:** Sign all executables and DLLs
5. **Timestamping:** Always use timestamping for long-term validity

## Troubleshooting

**Error: "The specified PFX password is not correct"**
- Verify the password matches the certificate export password

**Error: "SignTool Error: No certificates were found"**
- Ensure the certificate is in the correct store
- Check certificate format (.pfx vs .cer)

**Warning: "This certificate has expired"**
- Renew your certificate
- Timestamping helps but certificate must be valid at signing time

## Next Steps

1. Purchase a code signing certificate from a trusted CA
2. Add certificate to GitHub Secrets
3. The workflow will automatically sign executables on build
4. Test the signed executable to ensure it works correctly
