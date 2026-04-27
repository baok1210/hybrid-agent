#!/bin/bash
# Test Hybrid Agent API

set -e

BASE_URL="http://localhost:8001"
API_KEY="hybrid-free-key-2026"

echo "🧪 Testing Hybrid Agent API..."
echo "================================"

# Test 1: Health check
echo ""
echo "1. Health check..."
HEALTH=$(curl -s "$BASE_URL/health" 2>/dev/null || echo '{"status":"error"}')
echo "   Response: $HEALTH"

# Test 2: List models
echo ""
echo "2. List models..."
curl -s "$BASE_URL/v1/models" 2>/dev/null | head -50 || echo "   Failed"

# Test 3: Chat completion
echo ""
echo "3. Chat completion test..."
echo "   Sending: 'Hello, what is 2+2?'"
echo ""

RESPONSE=$(curl -s -X POST "$BASE_URL/v1/chat/completions"   -H "Content-Type: application/json"   -H "Authorization: Bearer $API_KEY"   -d '{"model": "hybrid-agent", "messages": [{"role": "user", "content": "What is 2+2?"}]}' 2>/dev/null)

echo "   Response:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"

# Test 4: Function calling
echo ""
echo "4. Function calling test..."

curl -s -X POST "$BASE_URL/v1/chat/completions"   -H "Content-Type: application/json"   -H "Authorization: Bearer $API_KEY"   -d '{
    "model": "hybrid-agent",
    "messages": [{"role": "user", "content": "Get weather for Hanoi"}],
    "tools": [{
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "Get weather for a location",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {"type": "string"},
            "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
          },
          "required": ["location"]
        }
      }
    }]
  }' 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "   Failed"

echo ""
echo "================================"
echo "✅ Test completed!"
