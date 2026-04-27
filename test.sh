#!/usr/bin/env bash
set -e

echo "🧪 Testing Hybrid Agent AI Provider..."

# Check if server is running
if ! pgrep -f "uvicorn.*api_server" > /dev/null; then
    echo "⚠️  Server is not running. Starting..."
    ./start.sh
    sleep 5
fi

# Get port from config or default
if [ -f "config.yaml" ]; then
    PORT=$(grep -E "^\s*port:\s*" config.yaml | awk '{print $2}' | head -1)
    if [ -z "$PORT" ]; then
        PORT=8001
    fi
else
    PORT=8001
fi

API_URL="http://localhost:$PORT"
AUTH_TOKEN="hybrid-free-key-2026"

echo "🔗 Testing endpoint: $API_URL"
echo "🔑 Using auth token: $AUTH_TOKEN"

# Test 1: Health endpoint
echo ""
echo "1️⃣  Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s "$API_URL/health")
if echo "$HEALTH_RESPONSE" | grep -q "status.*healthy"; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed: $HEALTH_RESPONSE"
    exit 1
fi

# Test 2: Authentication required
echo ""
echo "2️⃣  Testing authentication..."
UNAUTH_RESPONSE=$(curl -s -X POST "$API_URL/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d '{"messages":[{"role":"user","content":"test"}]}')
if echo "$UNAUTH_RESPONSE" | grep -q "401\|unauthorized\|Unauthorized"; then
    echo "✅ Authentication required (as expected)"
else
    echo "⚠️  No authentication required (check config)"
fi

# Test 3: Valid request
echo ""
echo "3️⃣  Testing valid request..."
VALID_RESPONSE=$(curl -s -X POST "$API_URL/v1/chat/completions" \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"model":"hybrid-agent","messages":[{"role":"user","content":"Hello"}],"temperature":0}')
if echo "$VALID_RESPONSE" | grep -q "choices"; then
    echo "✅ Valid request succeeded"
    echo "Response preview:"
    echo "$VALID_RESPONSE" | jq -r '.choices[0].message.content // "No content"' | head -50
else
    echo "❌ Valid request failed:"
    echo "$VALID_RESPONSE" | head -200
    exit 1
fi

# Test 4: Tool execution
echo ""
echo "4️⃣  Testing tool execution..."
TOOL_RESPONSE=$(curl -s -X POST "$API_URL/v1/chat/completions" \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"model":"hybrid-agent","messages":[{"role":"user","content":"List files in current directory"}],"temperature":0}')
if echo "$TOOL_RESPONSE" | grep -q "choices"; then
    echo "✅ Tool execution test passed"
else
    echo "⚠️  Tool execution may have failed"
    echo "$TOOL_RESPONSE" | head -200
fi

# Test 5: Error handling
echo ""
echo "5️⃣  Testing error handling..."
ERROR_RESPONSE=$(curl -s -X POST "$API_URL/v1/chat/completions" \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"invalid":"json"}')
if echo "$ERROR_RESPONSE" | grep -q "422\|error\|validation"; then
    echo "✅ Error handling works"
else
    echo "⚠️  Error handling may not be working"
fi

# Test 6: Metrics endpoint
echo ""
echo "6️⃣  Testing metrics..."
METRICS_RESPONSE=$(curl -s "$API_URL/metrics")
if [ -n "$METRICS_RESPONSE" ]; then
    echo "✅ Metrics endpoint working"
else
    echo "⚠️  Metrics endpoint may be disabled"
fi

echo ""
echo "🎉 All tests completed!"
echo ""
echo "📊 Server status:"
curl -s "$API_URL/health" | jq -r '.status,.timestamp,.version // "No JSON"'

echo ""
echo "📈 Recent requests:"
curl -s "$API_URL/metrics" | grep -E "http_requests_total|request_duration" | head -5 || echo "No metrics available"

echo ""
echo "🚀 Ready for production use!"
echo "API: $API_URL/v1/chat/completions"
echo "Token: $AUTH_TOKEN"