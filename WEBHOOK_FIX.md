# GitHub Webhook HTTPS→HTTP Fix

## Problem
```
Error: "http: server gave HTTP response to HTTPS client"
```

Jenkins listens on **HTTP** (port 8080) but GitHub tries to deliver webhook via **HTTPS**.

## Solution

### Step 1: Edit GitHub Webhook URL
1. Go to your GitHub repo
2. Settings → Webhooks
3. Click the webhook you configured
4. Change Payload URL:
   - **FROM:** `https://<EC2_IP>:8080/github-webhook/`
   - **TO:** `http://<EC2_IP>:8080/github-webhook/`
5. Click **Update webhook**

### Step 2: Test Delivery
1. Scroll down to "Recent Deliveries"
2. Click on a failed delivery (red ✗)
3. Click **Redeliver**
4. Jenkins should trigger the pipeline (~5-10 seconds)
5. GitHub should show green ✓ (200 OK response)

### Step 3: Verify in Jenkins
1. Go to `http://<EC2_IP>:8080`
2. Click your Pipeline job
3. Should show a new build in the Build History (Started by GitHub push)
4. Wait ~2-3 minutes for tests to complete
5. Check console output and email notification

## Why This Works
- GitHub webhook requires HTTPS for security (enforced)
- But Jenkins HTTP endpoint is at `8080/github-webhook/` (not HTTPS)
- Changing URL to `http://` tells GitHub to send unencrypted JSON payload
- Jenkins accepts it on the HTTP endpoint and triggers the pipeline

## For Production
If you want HTTPS in the future, set up:
- SSL certificate (Let's Encrypt via certbot)
- Reverse proxy (nginx) with SSL → Jenkins HTTP
- Or configure Jenkins with built-in SSL support

For now, **HTTP is fine for EC2 testing**.
