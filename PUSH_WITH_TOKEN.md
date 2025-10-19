# 🔑 Push to GitHub Using Personal Access Token

Since browser authentication isn't working, you need to use a **Personal Access Token (PAT)**.

---

## 📝 Step 1: Create a Personal Access Token

### 1. Go to GitHub Token Settings
**Open this link:** https://github.com/settings/tokens/new

### 2. Fill in Token Details
- **Note:** `VAMedRec Development Token`
- **Expiration:** 90 days (or your preference)
- **Select scopes:** Check the following:
  - ✅ `repo` (Full control of private repositories)
    - ✅ repo:status
    - ✅ repo_deployment
    - ✅ public_repo
    - ✅ repo:invite
    - ✅ security_events
  - ✅ `workflow` (Update GitHub Action workflows)

### 3. Generate Token
1. Scroll to bottom
2. Click **"Generate token"**
3. **COPY THE TOKEN IMMEDIATELY** (you won't see it again!)
   - It looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

## 🚀 Step 2: Push Using the Token

### Option A: Push with Token (One-time)

Run this command and use your token as the password:

```powershell
git push -u origin master
```

When prompted:
- **Username:** `cyber3pxVA`
- **Password:** `paste-your-token-here` (paste the token you just created)

### Option B: Store Credentials (Recommended)

Windows will remember your token:

```powershell
# Configure Git to use Windows Credential Manager
git config --global credential.helper wincred

# Now push (you'll be prompted once)
git push -u origin master
```

When prompted:
- **Username:** `cyber3pxVA`
- **Password:** `paste-your-token-here`

Windows will store it and you won't be prompted again!

---

## 🔐 Step 3: Alternative - Use Token in URL

You can also embed the token in the remote URL (less secure, but works):

```powershell
# Remove old remote
git remote remove origin

# Add remote with token
git remote add origin https://ghp_YOUR_TOKEN_HERE@github.com/cyber3pxVA/vamedrec.git

# Push
git push -u origin master
```

**Replace `ghp_YOUR_TOKEN_HERE` with your actual token!**

---

## 🧪 Quick Test Commands

### After setting up token, verify:

```powershell
# 1. Check remote
git remote -v

# 2. Test authentication
git ls-remote origin

# 3. Push to GitHub
git push -u origin master
```

---

## 🎯 Complete Setup Script

Copy and run this (replace TOKEN with your actual token):

```powershell
# Navigate to project
cd "c:\Users\VHAWRJDRESCF\OneDrive - Department of Veterans Affairs\Documents\GitHub\med-reconciliation"

# Configure credential helper
git config --global credential.helper wincred

# Push to GitHub (will prompt for username and token)
git push -u origin master
```

**When prompted:**
- Username: `cyber3pxVA`
- Password: `[paste your token]`

---

## ✅ Success Indicators

After successful push, you should see:

```
Enumerating objects: 52, done.
Counting objects: 100% (52/52), done.
Delta compression using up to 8 threads
Compressing objects: 100% (43/43), done.
Writing objects: 100% (52/52), 65.34 KiB | 3.63 MiB/s, done.
Total 52 (delta 8), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (8/8), done.
To https://github.com/cyber3pxVA/vamedrec.git
 * [new branch]      master -> master
Branch 'master' set up to track remote branch 'master' from 'origin'.
```

---

## 🔒 Security Notes

✅ **DO:**
- Store token securely
- Use Windows Credential Manager
- Set token expiration
- Use minimal required scopes

❌ **DON'T:**
- Share your token
- Commit token to code
- Use token with full permissions if not needed

---

## 🆘 Troubleshooting

### "Authentication Failed"
- Verify token is correct
- Check token hasn't expired
- Ensure `repo` scope is selected

### "Permission Denied"
- Verify you have write access to the repo
- Check token has `workflow` scope for GitHub Actions

### "Remote Already Exists"
```powershell
git remote remove origin
git remote add origin https://github.com/cyber3pxVA/vamedrec.git
git push -u origin master
```

---

## 📞 Next Steps After Push

1. ✅ Verify files on GitHub: https://github.com/cyber3pxVA/vamedrec
2. ✅ Check that `.env` is NOT visible
3. ✅ Confirm `.env.example` IS visible
4. ✅ Set up Docker Hub secrets in GitHub Actions
5. ✅ Watch automated builds run

---

**Ready? Create your token and let's push!** 🚀

**Token URL:** https://github.com/settings/tokens/new
