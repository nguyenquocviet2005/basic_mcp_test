#!/bin/bash

# Deployment script for MCP Server on EC2

echo "🚀 Starting MCP Server deployment..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install dependencies
echo "🔧 Installing system dependencies..."
sudo apt install python3 python3-pip python3-venv nginx git -y

# Clone repository (if not exists)
if [ ! -d "basic_mcp_test" ]; then
    echo "📥 Cloning repository..."
    git clone https://github.com/nguyenquocviet2005/basic_mcp_test.git
fi

cd basic_mcp_test

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Copy systemd service file
echo "⚙️ Setting up systemd service..."
sudo cp mcp-server.service /etc/systemd/system/

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable mcp-server
sudo systemctl start mcp-server

# Check service status
echo "📊 Checking service status..."
sudo systemctl status mcp-server

# Configure nginx (optional)
echo "🌐 Configuring nginx..."
sudo tee /etc/nginx/sites-available/mcp-server <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable nginx site
sudo ln -sf /etc/nginx/sites-available/mcp-server /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl restart nginx

echo "✅ Deployment completed!"
echo "🌍 Server should be accessible at: http://$(curl -s ifconfig.me)"
echo "📊 Check service status: sudo systemctl status mcp-server"
echo "📝 View logs: sudo journalctl -u mcp-server -f"
