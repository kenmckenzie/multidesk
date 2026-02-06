# Troubleshooting MultiDesk Build Issues

## If the executable doesn't run after compilation

### Quick Checks

1. **Run the diagnostic script:**
   ```powershell
   .\check_multidesk.ps1
   ```

2. **Check for missing sciter.dll:**
   - The executable requires `sciter.dll` in the same directory
   - Download from: https://raw.githubusercontent.com/c-smile/sciter-sdk/master/bin.win/x64/sciter.dll
   - Place it next to `multidesk.exe`

3. **Check Visual C++ Runtime:**
   - Install Visual C++ Redistributable: https://aka.ms/vs/17/release/vc_redist.x64.exe

4. **Run from Command Prompt to see errors:**
   ```cmd
   cd path\to\multidesk
   multidesk.exe
   ```
   This will show any error messages that might be hidden when double-clicking.

### Common Issues

#### Issue: "The code execution cannot proceed because sciter.dll was not found"
**Solution:** Download sciter.dll and place it in the same directory as multidesk.exe

#### Issue: "The application was unable to start correctly (0xc000007b)"
**Solution:** Install Visual C++ Redistributable (see link above)

#### Issue: "VCRUNTIME140.dll was not found" or "MSVCP140.dll was not found"
**Solution:** Install Visual C++ Redistributable (see link above)

#### Issue: Executable runs but shows nothing / crashes immediately
**Solution:** 
1. Check Windows Event Viewer for detailed error messages
2. Run from command prompt to see console output
3. Check if antivirus is blocking it

### Check GitHub Actions Build

1. Go to: https://github.com/kenmckenzie/multidesk/actions
2. Click on the latest "Build MultiDesk (Windows)" workflow run
3. Check if all steps completed successfully
4. Download the artifact and verify both files are present:
   - `multidesk.exe`
   - `sciter.dll`

### Next Steps

After the workflow is updated, it will automatically include sciter.dll in the artifact. Until then:
1. Download the artifact from GitHub Actions
2. Download sciter.dll separately
3. Place both files in the same directory
4. Run multidesk.exe
