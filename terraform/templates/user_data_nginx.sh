#!/bin/bash
set -e

# Update system
yum update -y

# Install Docker
amazon-linux-extras install docker -y
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Nginx
amazon-linux-extras install nginx1 -y

# Create nginx configuration directory
mkdir -p /etc/nginx/conf.d

# Create basic reverse proxy configuration
cat > /etc/nginx/conf.d/upstream.conf << 'EOF'
# Upstream for microservices
upstream chat_service {
    server ${CHAT_SERVICE_HOST}:8000;
}

upstream user_management_service {
    server ${USER_MGMT_SERVICE_HOST}:8001;
}

upstream document_service {
    server ${DOCUMENT_SERVICE_HOST}:8002;
}

upstream quiz_service {
    server ${QUIZ_SERVICE_HOST}:8003;
}
EOF

# Create main server configuration
cat > /etc/nginx/conf.d/api.conf << 'EOF'
server {
    listen 80;
    server_name _;

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # Chat service routes
    location /api/chat {
        proxy_pass http://chat_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # User management service routes
    location /api/users {
        proxy_pass http://user_management_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/auth {
        proxy_pass http://user_management_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Document service routes
    location /api/documents {
        proxy_pass http://document_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 50M;
    }

    # Quiz service routes
    location /api/quiz {
        proxy_pass http://quiz_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Start and enable Nginx
systemctl start nginx
systemctl enable nginx

# Install CloudWatch agent (optional)
yum install amazon-cloudwatch-agent -y

# Log completion
echo "Nginx gateway setup completed at $(date)" > /var/log/user-data-complete.log

