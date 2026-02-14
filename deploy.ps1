# Quick Deployment Script
# Run this to deploy to Netlify in 30 seconds

Write-Host "MedLit AI - Quick Deploy" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green
Write-Host ""

# Check if web folder exists
if (-not (Test-Path "web\index.html")) {
    Write-Host "ERROR: web/index.html not found!" -ForegroundColor Red
    exit 1
}

Write-Host "Files ready for deployment:" -ForegroundColor Yellow
Write-Host "  - web/index.html (Landing page)" -ForegroundColor Gray
Write-Host "  - web/samples.html (Sample digests)" -ForegroundColor Gray
Write-Host ""

Write-Host "DEPLOYMENT OPTIONS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. NETLIFY DROP (Easiest - 30 seconds)" -ForegroundColor Green
Write-Host "   a. Go to: https://app.netlify.com/drop" -ForegroundColor White
Write-Host "   b. Drag the 'web' folder onto the page" -ForegroundColor White
Write-Host "   c. Get instant URL like: https://medlit-ai-123.netlify.app" -ForegroundColor White
Write-Host ""

Write-Host "2. SURGE.SH (Command line)" -ForegroundColor Green
Write-Host "   npm install -g surge" -ForegroundColor White
Write-Host "   cd web" -ForegroundColor White
Write-Host "   surge" -ForegroundColor White
Write-Host "   Choose domain: medlit-ai.surge.sh" -ForegroundColor White
Write-Host ""

Write-Host "3. VERCEL" -ForegroundColor Green
Write-Host "   npm install -g vercel" -ForegroundColor White
Write-Host "   cd web" -ForegroundColor White
Write-Host "   vercel --prod" -ForegroundColor White
Write-Host ""

Write-Host "RECOMMENDED: Use Netlify Drop for instant deployment." -ForegroundColor Yellow
Write-Host ""

# Create a zip for easy upload
Compress-Archive -Path "web\*" -DestinationPath "medlit-ai-deploy.zip" -Force
Write-Host "Created: medlit-ai-deploy.zip (ready to upload to Netlify)" -ForegroundColor Green
