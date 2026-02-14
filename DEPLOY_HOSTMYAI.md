# Deploy to hostmyai.app

## Files to Upload

Upload these files to your hostmyai.app hosting:

1. **index.html** → https://hostmyai.app/
2. **samples.html** → https://hostmyai.app/samples

## Quick Upload Methods

### Option 1: FTP/SFTP
If you have FTP access:
```
Host: hostmyai.app (or ftp.hostmyai.app)
Username: your_username
Password: your_password
Port: 21 (FTP) or 22 (SFTP)
```

Upload `index.html` to `/public_html/` or `/www/`
Upload `samples.html` to `/public_html/samples` or `/www/samples`

### Option 2: cPanel File Manager
1. Login to cPanel (usually: hostmyai.app:2083 or hostmyai.app/cpanel)
2. Go to **File Manager**
3. Navigate to `public_html/` folder
4. Click **Upload**
5. Select `index.html`
6. Create folder `samples` and upload `samples.html` there

### Option 3: SSH/SCP
```bash
# Upload index.html
scp index.html user@hostmyai.app:/var/www/html/

# Upload samples.html
scp samples.html user@hostmyai.app:/var/www/html/samples/
```

### Option 4: Hosting Control Panel
Most hosting providers have a web-based file manager:
1. Login to your hosting account
2. Find "File Manager" or "Files"
3. Upload the HTML files to the web root

---

## File Structure on Server

```
/public_html/           (or /www/ or /htdocs/)
├── index.html          → https://hostmyai.app/
└── samples/
    └── index.html      → https://hostmyai.app/samples
    
OR (if no subfolder):

/public_html/
├── index.html          → https://hostmyai.app/
└── samples.html        → https://hostmyai.app/samples.html
```

---

## Testing

After upload, check:

1. **Homepage**: https://hostmyai.app
   - Loads correctly
   - All buttons work
   - Telegram link works
   - WhatsApp link works

2. **Samples page**: https://hostmyai.app/samples
   - Loads correctly
   - All 4 sample digests visible
   - Back to home link works

3. **Mobile**: Test on your phone
   - Responsive design
   - Buttons clickable
   - Text readable

---

## Troubleshooting

### 404 Error on /samples
If `https://hostmyai.app/samples` gives 404:

**Option A**: Rename `samples.html` to `index.html` and put in `samples/` folder

**Option B**: Access as `https://hostmyai.app/samples.html`

### Styles not loading
If page looks unstyled:
- Check that CSS is inline (it is in our files)
- Clear browser cache (Ctrl+Shift+R)

### Links not working
- Check Telegram link: https://t.me/MedJournal_bot
- Check WhatsApp: Update with your actual number

---

## Post-Deployment Checklist

- [ ] https://hostmyai.app loads landing page
- [ ] https://hostmyai.app/samples loads samples
- [ ] Telegram bot link works
- [ ] WhatsApp link works (update your number first)
- [ ] Mobile responsive
- [ ] Page speed is good

---

## Next Steps After Deployment

1. **Share the link**:
   ```
   🩺 MedLit AI - Daily medical research digests for doctors
   
   https://hostmyai.app
   
   ₹299/month • Free 7-day trial • Powered by OpenAlex
   ```

2. **Update social profiles**:
   - LinkedIn: Add to bio
   - Twitter: Pin tweet with link
   - WhatsApp Status: Share link

3. **Get first customers**:
   - Share in doctor WhatsApp groups
   - LinkedIn post with link
   - Email to doctor friends

---

Your landing page is ready to deploy!
