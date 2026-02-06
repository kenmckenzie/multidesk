# Avoiding Antivirus False Positives

This document outlines strategies to reduce the likelihood of MultiDesk being flagged as malicious by antivirus software.

## Code Signing (Most Important)

**Code signing is the single most effective way to avoid false positives.**

1. **Obtain a Code Signing Certificate:**
   - Purchase from a trusted Certificate Authority (CA) like DigiCert, Sectigo, or GlobalSign
   - Cost: Typically $200-500/year for standard certificates
   - EV (Extended Validation) certificates provide better trust but cost more ($400-800/year)

2. **Sign the Executable:**
   - Sign `multidesk.exe` after compilation
   - Sign `sciter.dll` as well
   - Use `signtool.exe` (included with Windows SDK):
     ```powershell
     signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com multidesk.exe
     ```

3. **Add to GitHub Actions Workflow:**
   - Store certificate securely as a GitHub secret
   - Add signing step after build, before artifact upload

## Build Configuration

1. **Use Release Builds:**
   - Always use `--release` flag (already done)
   - Optimized binaries are less suspicious than debug builds

2. **Static Linking:**
   - Link dependencies statically when possible
   - Reduces DLL dependencies that might trigger warnings

3. **Avoid Obfuscation:**
   - Don't use packers, encryptors, or code obfuscation
   - These techniques are red flags for antivirus software

## Distribution Best Practices

1. **Legitimate Distribution Channels:**
   - Host on GitHub Releases (already done)
   - Consider official website with HTTPS
   - Avoid file-sharing sites or suspicious sources

2. **Transparency:**
   - Publish source code (already done)
   - Document what the application does
   - Provide clear installation instructions

3. **Version Information:**
   - Include proper version info in the executable (already configured in Cargo.toml)
   - Set proper file description and company name

## Application Behavior

1. **Avoid Suspicious Patterns:**
   - Don't hide processes or use stealth techniques
   - Don't modify critical system files unnecessarily
   - Don't access sensitive data without user consent

2. **Clear Purpose:**
   - Application name and description should clearly indicate it's a remote desktop tool
   - Don't use generic or suspicious names

3. **User Consent:**
   - Request permissions explicitly
   - Show what the application is doing
   - Provide clear privacy policy

## Submission to Antivirus Vendors

If you still get false positives:

1. **Submit to VirusTotal:**
   - Upload your executable to https://www.virustotal.com
   - Review which vendors flag it

2. **Contact Vendors Directly:**
   - Most major antivirus vendors have false positive reporting forms
   - Provide:
     - SHA256 hash of the file
     - Description of what the application does
     - Link to source code
     - Code signing certificate info (if available)

3. **Major Vendors:**
   - **Windows Defender:** https://www.microsoft.com/en-us/wdsi/filesubmission
   - **Norton/Symantec:** https://submit.norton.com/
   - **McAfee:** https://www.mcafee.com/enterprise/en-us/threat-center/submit-sample.html
   - **Kaspersky:** https://opentip.kaspersky.com/

## Current Implementation

The current build already includes:
- ✅ Release builds with optimizations
- ✅ Proper version information in Cargo.toml
- ✅ Static linking of dependencies via vcpkg
- ✅ Transparent source code on GitHub
- ✅ Legitimate distribution via GitHub Actions

**Next Step:** Implement code signing for maximum protection against false positives.

## Resources

- [Microsoft Code Signing Guide](https://docs.microsoft.com/en-us/windows-hardware/drivers/dashboard/get-a-code-signing-certificate)
- [RustDesk Build Documentation](https://rustdesk.com/docs/en/dev/build/windows/)
- [VirusTotal](https://www.virustotal.com)
