#!/bin/bash
set -e

# Update system
yum update -y

# Install Java (required for Kafka and Zookeeper)
yum install java-11-amazon-corretto-headless -y

# Create kafka user
useradd -r -s /bin/bash kafka || true

# Download and install Kafka
KAFKA_VERSION="3.6.0"
SCALA_VERSION="2.13"
cd /opt
wget "https://downloads.apache.org/kafka/$KAFKA_VERSION/kafka_$${SCALA_VERSION}-$KAFKA_VERSION.tgz"
tar -xzf kafka_$${SCALA_VERSION}-$KAFKA_VERSION.tgz
mv kafka_$${SCALA_VERSION}-$KAFKA_VERSION kafka
rm kafka_$${SCALA_VERSION}-$KAFKA_VERSION.tgz

# Create data directories
mkdir -p /var/lib/zookeeper
mkdir -p /var/lib/kafka-logs
chown -R kafka:kafka /var/lib/zookeeper
chown -R kafka:kafka /var/lib/kafka-logs
chown -R kafka:kafka /opt/kafka

# Mount additional EBS volume if exists
if [ -e /dev/xvdf ]; then
    mkfs -t ext4 /dev/xvdf
    mkdir -p /mnt/kafka-data
    mount /dev/xvdf /mnt/kafka-data
    echo '/dev/xvdf /mnt/kafka-data ext4 defaults,nofail 0 2' >> /etc/fstab
    mkdir -p /mnt/kafka-data/logs
    chown -R kafka:kafka /mnt/kafka-data
    ln -sf /mnt/kafka-data/logs /var/lib/kafka-logs
fi

# Configure Zookeeper
cat > /opt/kafka/config/zookeeper.properties << 'EOF'
dataDir=/var/lib/zookeeper
clientPort=2181
maxClientCnxns=0
admin.enableServer=false
tickTime=2000
initLimit=10
syncLimit=5
# For multi-node setup (uncomment and configure):
# server.1=zk1:2888:3888
# server.2=zk2:2888:3888
# server.3=zk3:2888:3888
EOF

# Configure Kafka
cat > /opt/kafka/config/server.properties << 'EOF'
# Broker ID (change for each broker)
broker.id=${BROKER_ID}

# Network settings
listeners=PLAINTEXT://:9092
advertised.listeners=PLAINTEXT://${PRIVATE_IP}:9092
num.network.threads=3
num.io.threads=8
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600

# Log settings
log.dirs=/var/lib/kafka-logs
num.partitions=3
num.recovery.threads.per.data.dir=1
offsets.topic.replication.factor=1
transaction.state.log.replication.factor=1
transaction.state.log.min.isr=1
log.retention.hours=168
log.segment.bytes=1073741824
log.retention.check.interval.ms=300000

# Zookeeper connection
zookeeper.connect=localhost:2181
zookeeper.connection.timeout.ms=18000

# Group coordinator settings
group.initial.rebalance.delay.ms=0
EOF

# Create systemd service for Zookeeper
cat > /etc/systemd/system/zookeeper.service << 'EOF'
[Unit]
Description=Apache Zookeeper
After=network.target

[Service]
Type=simple
User=kafka
Group=kafka
ExecStart=/opt/kafka/bin/zookeeper-server-start.sh /opt/kafka/config/zookeeper.properties
ExecStop=/opt/kafka/bin/zookeeper-server-stop.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create systemd service for Kafka
cat > /etc/systemd/system/kafka.service << 'EOF'
[Unit]
Description=Apache Kafka
After=network.target zookeeper.service
Requires=zookeeper.service

[Service]
Type=simple
User=kafka
Group=kafka
Environment="KAFKA_HEAP_OPTS=-Xmx512M -Xms512M"
ExecStart=/opt/kafka/bin/kafka-server-start.sh /opt/kafka/config/server.properties
ExecStop=/opt/kafka/bin/kafka-server-stop.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload

# Start services
systemctl start zookeeper
systemctl enable zookeeper
sleep 10
systemctl start kafka
systemctl enable kafka

# Wait for Kafka to be ready
sleep 30

# Create topics
TOPICS=(
    "document.uploaded"
    "document.processed"
    "notes.generated"
    "quiz.requested"
    "quiz.generated"
    "audio.transcription.requested"
    "audio.transcription.completed"
    "audio.generation.requested"
    "audio.generation.completed"
    "chat.message"
)

for topic in "$${TOPICS[@]}"; do
    /opt/kafka/bin/kafka-topics.sh --create \
        --bootstrap-server localhost:9092 \
        --replication-factor 1 \
        --partitions 3 \
        --topic "$topic" \
        --if-not-exists || true
done

# Install CloudWatch agent
yum install amazon-cloudwatch-agent -y

# Log completion
echo "Kafka setup completed at $(date)" > /var/log/user-data-complete.log
echo "Topics created:" >> /var/log/user-data-complete.log
/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092 >> /var/log/user-data-complete.log

