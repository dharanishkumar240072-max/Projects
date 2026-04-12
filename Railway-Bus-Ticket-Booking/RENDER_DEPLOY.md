# Deploy to Render.com

## Method 1: Using render.yaml (Recommended)

1. **Go to [render.com](https://render.com)** and sign up/login
2. **Click "New +"** → **"Blueprint"**
3. **Connect your GitHub repository**: `https://github.com/dharanishkumar240072-max/Railway-Bus-Ticket-Booking`
4. **Render will automatically detect render.yaml** and create both services
5. **Deploy both services**

## Method 2: Manual Deployment

### Deploy Backend:
1. **New +** → **Web Service**
2. **Connect GitHub repo**
3. **Settings**:
   - Name: `railway-booking-backend`
   - Environment: `Python 3`
   - Build Command: `cd Backend && pip install -r requirements.txt`
   - Start Command: `cd Backend && python app.py`
   - Instance Type: `Free`

### Deploy Frontend:
1. **New +** → **Static Site**
2. **Connect GitHub repo**
3. **Settings**:
   - Name: `railway-booking-frontend`
   - Build Command: `echo "No build needed"`
   - Publish Directory: `Frontend`

## Important Notes:
- Backend will be at: `https://railway-booking-backend.onrender.com`
- Frontend will be at: `https://railway-booking-frontend.onrender.com`
- Free tier may have cold starts (30-60 seconds delay)
- Update CORS settings if needed

## Environment Variables (if needed):
- `FLASK_ENV=production`
- `PORT=5000` (Render sets this automatically)