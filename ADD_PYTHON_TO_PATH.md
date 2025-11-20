# How to Add Python to PATH (Windows)

## Quick Steps:

1. **Press `Windows Key + X`** → Select **"System"**

2. Click **"Advanced system settings"** (on the right side)

3. Click **"Environment Variables"** button (at the bottom)

4. Under **"User variables"** section, find **"Path"** and click **"Edit"**

5. Click **"New"** and add these two paths:
   - `C:\Users\priya\AppData\Local\Programs\Python\Python312`
   - `C:\Users\priya\AppData\Local\Programs\Python\Python312\Scripts`

6. Click **"OK"** on all windows

7. **Close and reopen** your PowerShell/terminal

8. Test it:
   ```powershell
   python --version
   pip --version
   ```

Now you can use `python` and `pip` directly without the full path!

