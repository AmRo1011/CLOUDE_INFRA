# ==============================================================================
# Full System Health Check - Cloud Learning Platform Phase 2
# PowerShell Version for Windows
# ==============================================================================

Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     Cloud Learning Platform - Full System Health Check            ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Configuration
$APP_NODE_1_IP = "10.0.1.195"
$APP_NODE_2_IP = "10.0.2.179"
$KAFKA_IP = "10.0.10.231"

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "  1️⃣  KAFKA HEALTH CHECK" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

# Check Kafka port
try {
    $connection = Test-NetConnection -ComputerName $KAFKA_IP -Port 9092 -WarningAction SilentlyContinue
    if ($connection.TcpTestSucceeded) {
        Write-Host "✅ Kafka Broker (${KAFKA_IP}:9092): REACHABLE" -ForegroundColor Green
    } else {
        Write-Host "❌ Kafka Broker (${KAFKA_IP}:9092): UNREACHABLE" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Kafka Broker (${KAFKA_IP}:9092): ERROR" -ForegroundColor Red
}

# Check Zookeeper port
try {
    $connection = Test-NetConnection -ComputerName $KAFKA_IP -Port 2181 -WarningAction SilentlyContinue
    if ($connection.TcpTestSucceeded) {
        Write-Host "✅ Zookeeper (${KAFKA_IP}:2181): REACHABLE" -ForegroundColor Green
    } else {
        Write-Host "❌ Zookeeper (${KAFKA_IP}:2181): UNREACHABLE" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Zookeeper (${KAFKA_IP}:2181): ERROR" -ForegroundColor Red
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "  2️⃣  APP NODE 1 - User Management & Chat" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

# User Management Service
try {
    $response = Invoke-RestMethod -Uri "http://${APP_NODE_1_IP}:8001/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ User Management (8001): $($response.status) - $($response.service) v$($response.version)" -ForegroundColor Green
} catch {
    Write-Host "❌ User Management (8001): FAILED" -ForegroundColor Red
}

# Chat Service
try {
    $response = Invoke-RestMethod -Uri "http://${APP_NODE_1_IP}:8000/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Chat Service (8000): $($response.status) - $($response.service) v$($response.version)" -ForegroundColor Green
} catch {
    Write-Host "❌ Chat Service (8000): FAILED" -ForegroundColor Red
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "  3️⃣  APP NODE 2 - Document & Quiz" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

# Document Service
try {
    $response = Invoke-RestMethod -Uri "http://${APP_NODE_2_IP}:8002/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Document Service (8002): $($response.status) - $($response.service) v$($response.version)" -ForegroundColor Green
} catch {
    Write-Host "❌ Document Service (8002): FAILED" -ForegroundColor Red
}

# Quiz Service
try {
    $response = Invoke-RestMethod -Uri "http://${APP_NODE_2_IP}:8003/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Quiz Service (8003): $($response.status) - $($response.service) v$($response.version)" -ForegroundColor Green
} catch {
    Write-Host "❌ Quiz Service (8003): FAILED" -ForegroundColor Red
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "  4️⃣  SYSTEM SUMMARY" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

Write-Host ""
Write-Host "Service Endpoints:" -ForegroundColor Cyan
Write-Host "  • User Management:  http://${APP_NODE_1_IP}:8001" -ForegroundColor White
Write-Host "  • Chat Service:     http://${APP_NODE_1_IP}:8000" -ForegroundColor White
Write-Host "  • Document Service: http://${APP_NODE_2_IP}:8002" -ForegroundColor White
Write-Host "  • Quiz Service:     http://${APP_NODE_2_IP}:8003" -ForegroundColor White
Write-Host ""
Write-Host "Infrastructure:" -ForegroundColor Cyan
Write-Host "  • Kafka Broker:     ${KAFKA_IP}:9092" -ForegroundColor White
Write-Host "  • Zookeeper:        ${KAFKA_IP}:2181" -ForegroundColor White
Write-Host ""

Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    Health Check Complete                           ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

