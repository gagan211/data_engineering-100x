#!/bin/bash
# Quick Start Guide for ETL Pipeline
# This script demonstrates step-by-step execution

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          DATA ENGINEERING ASSESSMENT - QUICK START            ║"
echo "╚════════════════════════════════════════════════════════════════╝"

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

echo ""
echo "📂 Project Directory: $REPO_DIR"
echo ""

# Step 1: Check Python
echo "═══════════════════════════════════════════════════════════════════"
echo "STEP 1: Verify Python Installation"
echo "═══════════════════════════════════════════════════════════════════"
python3 --version || (echo "❌ Python 3 not found" && exit 1)
echo "✓ Python installed"
echo ""

# Step 2: Install dependencies
echo "═══════════════════════════════════════════════════════════════════"
echo "STEP 2: Install Python Dependencies"
echo "═══════════════════════════════════════════════════════════════════"
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Step 3: Check Docker
echo "═══════════════════════════════════════════════════════════════════"
echo "STEP 3: Verify Docker Installation"
echo "═══════════════════════════════════════════════════════════════════"
docker --version || (echo "❌ Docker not found" && exit 1)
echo "✓ Docker installed"
echo ""

# Step 4: Start MySQL
echo "═══════════════════════════════════════════════════════════════════"
echo "STEP 4: Start MySQL Container"
echo "═══════════════════════════════════════════════════════════════════"
echo "Starting: docker-compose -f docker-compose.initial.yml up --build -d"
docker-compose -f docker-compose.initial.yml up --build -d
echo "⏳ Waiting for MySQL to be ready..."
sleep 5
echo "✓ MySQL container started"
echo ""

# Step 5: Verify connectivity
echo "═══════════════════════════════════════════════════════════════════"
echo "STEP 5: Verify MySQL Connectivity"
echo "═══════════════════════════════════════════════════════════════════"
mysql -h localhost -u db_user -p6equj5_db_user -e "SELECT VERSION();" 2>/dev/null || \
    (echo "❌ MySQL connection failed" && exit 1)
echo "✓ MySQL connection successful"
echo ""

# Step 6: Run ETL
echo "═══════════════════════════════════════════════════════════════════"
echo "STEP 6: Execute ETL Pipeline"
echo "═══════════════════════════════════════════════════════════════════"
python src/etl/run_etl.py
echo ""

# Step 7: Verify data
echo "═══════════════════════════════════════════════════════════════════"
echo "STEP 7: Verify Data Loaded"
echo "═══════════════════════════════════════════════════════════════════"
cat << 'EOF' | mysql -h localhost -u db_user -p6equj5_db_user home_db
SELECT 'properties' as table_name, COUNT(*) as row_count FROM properties
UNION ALL
SELECT 'valuations', COUNT(*) FROM valuations
UNION ALL
SELECT 'hoa_fees', COUNT(*) FROM hoa_fees
UNION ALL
SELECT 'rehab_assessments', COUNT(*) FROM rehab_assessments;
EOF
echo "✓ Data verification complete"
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                     ✓ SUCCESS!                                ║"
echo "║                                                                ║"
echo "║  ETL Pipeline completed successfully!                         ║"
echo "║  Check etl_pipeline.log for detailed execution logs.          ║"
echo "║                                                                ║"
echo "║  Database: home_db                                            ║"
echo "║  Host: localhost:3306                                         ║"
echo "║  User: db_user                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
