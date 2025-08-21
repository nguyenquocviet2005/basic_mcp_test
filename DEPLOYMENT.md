# 🚀 MCP Server Deployment Guide

## Overview
This guide will help you deploy your MCP server to AWS EC2 and set up CI/CD with GitHub Actions.

## 📋 Prerequisites
- AWS Account with EC2 access
- GitHub repository with your MCP server code
- SSH key pair for EC2 access

## 🏗️ Step 1: Launch EC2 Instance

### 1.1 Create EC2 Instance
1. Go to AWS Console → EC2 → Launch Instance
2. **Name**: `mcp-server`
3. **AMI**: Ubuntu Server 22.04 LTS (free tier eligible)
4. **Instance Type**: `t2.micro` (free tier) or `t3.small`
5. **Key Pair**: Create new key pair, download `.pem` file

### 1.2 Configure Security Group
Create new security group with these rules:
- **SSH (22)**: Your IP address only
- **HTTP (80)**: 0.0.0.0/0 (for nginx)
- **Custom TCP (8000)**: 0.0.0.0/0 (for MCP server)

### 1.3 Launch Instance
- Click "Launch Instance"
- Wait for instance to be running
- Note the **Public IPv4 address**

## 🔑 Step 2: Connect to EC2

### 2.1 Prepare SSH Key
```bash
# Make key file executable
chmod 400 your-key.pem

# Connect to EC2
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

### 2.2 Initial Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install basic tools
sudo apt install curl wget git -y
```

## 🚀 Step 3: Deploy MCP Server

### 3.1 Clone Repository
```bash
# Clone your repo
git clone https://github.com/nguyenquocviet2005/basic_mcp_test.git
cd basic_mcp_test
```

### 3.2 Run Deployment Script
```bash
# Make script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### 3.3 Manual Setup (Alternative)
If you prefer manual setup:
```bash
# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv nginx -y

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Set up systemd service
sudo cp mcp-server.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mcp-server
sudo systemctl start mcp-server
```

## ⚙️ Step 4: Configure GitHub Actions

### 4.1 Add Repository Secrets
Go to your GitHub repo → Settings → Secrets and variables → Actions

Add these secrets:
- **`EC2_HOST`**: Your EC2 public IP address
- **`EC2_USERNAME`**: `ubuntu`
- **`EC2_SSH_KEY`**: Your private SSH key content (the .pem file content)
- **`EC2_PORT`**: `22`

### 4.2 How to Get SSH Key Content
```bash
# On your local machine
cat your-key.pem
# Copy the entire content (including BEGIN and END lines)
```

### 4.3 Test GitHub Actions
1. Make a change to your code
2. Commit and push to main branch
3. Go to Actions tab to see deployment progress

## 🔍 Step 5: Verify Deployment

### 5.1 Check Service Status
```bash
# Check MCP server status
sudo systemctl status mcp-server

# View logs
sudo journalctl -u mcp-server -f
```

### 5.2 Test Endpoints
```bash
# Test MCP endpoint
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "initialize", "id": 1}'

# Test HTTP endpoint (if using nginx)
curl http://YOUR_EC2_PUBLIC_IP/stream?message=hello
```

### 5.3 Check Ports
```bash
# Check what's listening
sudo netstat -tlnp | grep :8000
sudo netstat -tlnp | grep :80
```

## 🛠️ Step 6: Troubleshooting

### 6.1 Common Issues

**Service won't start:**
```bash
# Check service logs
sudo journalctl -u mcp-server -f

# Check if port is in use
sudo netstat -tlnp | grep :8000
```

**Permission denied:**
```bash
# Fix file permissions
sudo chown -R ubuntu:ubuntu /home/ubuntu/basic_mcp_test
chmod +x /home/ubuntu/basic_mcp_test/venv/bin/python
```

**Port not accessible:**
```bash
# Check security group rules
# Ensure port 8000 is open in EC2 security group
```

### 6.2 Useful Commands
```bash
# Restart service
sudo systemctl restart mcp-server

# Reload systemd
sudo systemctl daemon-reload

# Check nginx status
sudo systemctl status nginx

# View nginx logs
sudo tail -f /var/log/nginx/error.log
```

## 🔄 Step 7: CI/CD Workflow

### 7.1 Automatic Deployment
- Every push to `main` branch triggers deployment
- GitHub Actions connects to EC2 via SSH
- Pulls latest code and restarts service

### 7.2 Manual Deployment
```bash
# On EC2
cd basic_mcp_test
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart mcp-server
```

## 📊 Step 8: Monitoring

### 8.1 Service Monitoring
```bash
# Check service health
sudo systemctl is-active mcp-server

# Monitor resource usage
htop
df -h
```

### 8.2 Log Monitoring
```bash
# Follow MCP server logs
sudo journalctl -u mcp-server -f

# Follow nginx logs
sudo tail -f /var/log/nginx/access.log
```

## 🎯 Next Steps

1. **Set up monitoring** with CloudWatch or similar
2. **Configure SSL** with Let's Encrypt
3. **Set up backups** for your EC2 instance
4. **Add health checks** to your MCP server
5. **Implement logging** to CloudWatch or external service

## 📞 Support

If you encounter issues:
1. Check service logs: `sudo journalctl -u mcp-server -f`
2. Verify security group rules
3. Check GitHub Actions logs
4. Ensure all dependencies are installed

---

**Happy Deploying! 🚀**
