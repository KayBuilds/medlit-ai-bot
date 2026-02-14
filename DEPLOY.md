# Deployment Guide - MedLit AI

## Option 1: Netlify (Recommended - Free & Fast)

### Step 1: Prepare Files
```bash
cd medlit-ai/web
# Files ready: index.html, samples.html
```

### Step 2: Deploy via Drag & Drop
1. Go to https://app.netlify.com/drop
2. Drag the `web/` folder onto the page
3. Get instant URL like `https://medlit-ai-123.netlify.app`
4. Done!

### Step 3: Custom Domain (Optional)
1. In Netlify dashboard → Domain settings
2. Add custom domain: `medlit.ai` or `medjournal.in`
3. Update DNS records as instructed

---

## Option 2: Vercel (Free, Great Performance)

### Step 1: Install Vercel CLI
```bash
npm i -g vercel
# Or use npx: npx vercel
```

### Step 2: Deploy
```bash
cd medlit-ai/web
vercel --prod
```

### Step 3: Follow prompts
- Login with GitHub/Google
- Confirm deployment
- Get URL: `https://medlit-ai.vercel.app`

---

## Option 3: GitHub Pages (Free, Simple)

### Step 1: Create GitHub Repo
1. Go to github.com/new
2. Name: `medlit-ai`
3. Make it public

### Step 2: Upload Files
```bash
cd medlit-ai/web
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOURNAME/medlit-ai.git
git push -u origin main
```

### Step 3: Enable GitHub Pages
1. Repo Settings → Pages
2. Source: Deploy from branch
3. Branch: main / root
4. Save
5. Site live at: `https://YOURNAME.github.io/medlit-ai`

---

## Option 4: Surge.sh (Easiest)

### Step 1: Install Surge
```bash
npm install -g surge
```

### Step 2: Deploy
```bash
cd medlit-ai/web
surge
# Enter domain: medlit-ai.surge.sh
# Done!
```

---

## Quick Test Locally

Before deploying, test locally:

```bash
cd medlit-ai
python serve.py
```

Then open:
- http://localhost:8000/index.html
- http://localhost:8000/samples.html

---

## Post-Deployment Checklist

- [ ] Landing page loads correctly
- [ ] Sample digests page works
- [ ] All links work (Telegram bot, samples)
- [ ] Mobile responsive (test on phone)
- [ ] Page speed is good (use PageSpeed Insights)

---

## Recommended: Netlify Drop (Fastest)

For immediate deployment without any setup:

1. Zip the `web/` folder
2. Go to https://app.netlify.com/drop
3. Upload the zip
4. Get URL in 30 seconds

**Use this for testing right now!**
