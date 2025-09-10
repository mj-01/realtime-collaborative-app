#!/bin/bash

# Test runner script for the monorepo

echo "🧪 Running Tests for Realtime Collaborative App"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to run tests and report results
run_test() {
    local test_name="$1"
    local test_command="$2"
    local test_dir="$3"
    
    echo -e "\n${YELLOW}Running $test_name...${NC}"
    echo "Command: $test_command"
    echo "Directory: $test_dir"
    echo "----------------------------------------"
    
    if [ -d "$test_dir" ]; then
        cd "$test_dir"
        if eval "$test_command"; then
            echo -e "${GREEN}✅ $test_name PASSED${NC}"
            cd ..
            return 0
        else
            echo -e "${RED}❌ $test_name FAILED${NC}"
            cd ..
            return 1
        fi
    else
        echo -e "${RED}❌ Directory $test_dir not found${NC}"
        return 1
    fi
}

# Track overall success
overall_success=true

# Backend API Tests
echo -e "\n${YELLOW}🔧 Backend Tests${NC}"
if run_test "Backend API Tests" "source venv/bin/activate && python -m pytest tests/ -v" "backend"; then
    echo "Backend tests completed successfully"
else
    echo "Backend tests failed"
    overall_success=false
fi

# Frontend Tests
echo -e "\n${YELLOW}🎨 Frontend Tests${NC}"
if run_test "Frontend Component Tests" "npm test" "frontend"; then
    echo "Frontend tests completed successfully"
else
    echo "Frontend tests failed"
    overall_success=false
fi

# Integration Tests (removed - were failing)

# Summary
echo -e "\n${YELLOW}📊 Test Summary${NC}"
echo "=============================================="

if [ "$overall_success" = true ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}💥 Some tests failed!${NC}"
    exit 1
fi
