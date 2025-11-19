#!/bin/bash

# Parallel Data Analysis Framework - Quick Start Script
# This script sets up and runs the framework for the first time

set -e  # Exit on error

echo "=================================================="
echo "Parallel Data Analysis Framework - Quick Start"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_success "Docker is installed"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    print_success "Docker Compose is installed"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_warning "Python 3 is not installed. Some features may not work."
    else
        print_success "Python 3 is installed"
    fi
    
    echo ""
}

# Create directory structure
create_directories() {
    print_info "Creating directory structure..."
    
    mkdir -p data/input
    mkdir -p data/sample
    mkdir -p output/general
    mkdir -p output/general/graphs
    mkdir -p output/statistics
    mkdir -p output/failures
    mkdir -p tests
    
    print_success "Directories created"
    echo ""
}

# Generate sample data
generate_sample_data() {
    print_info "Generating sample data..."
    
    if command -v python3 &> /dev/null; then
        python3 example_test.py generate
        print_success "Sample data generated"
    else
        print_warning "Python 3 not available. Skipping sample data generation."
    fi
    
    echo ""
}

# Build Docker images
build_images() {
    print_info "Building Docker images..."
    print_warning "This may take several minutes..."
    
    docker-compose build
    
    print_success "Docker images built successfully"
    echo ""
}

# Start the cluster
start_cluster() {
    print_info "Starting Spark cluster..."
    
    docker-compose up -d
    
    print_info "Waiting for cluster to be ready (15 seconds)..."
    sleep 15
    
    print_success "Spark cluster started!"
    echo ""
    echo "Web UIs available at:"
    echo "  - Spark Master:  http://localhost:8080"
    echo "  - Spark App:     http://localhost:4040"
    echo "  - Worker 1:      http://localhost:8081"
    echo "  - Worker 2:      http://localhost:8082"
    echo "  - Worker 3:      http://localhost:8083"
    echo ""
}

# Run sample analysis
run_sample_analysis() {
    print_info "Running sample analysis..."
    
    if [ -f "data/input/sample_sales.csv" ]; then
        docker exec -it spark-master python3 -m src.main \
            --input /app/data/input/sample_sales.csv \
            --master spark://spark-master:7077 \
            --analysis full
        
        print_success "Analysis completed!"
        echo ""
        echo "Results saved in:"
        echo "  - output/general/          : Analysis results and graphs"
        echo "  - output/statistics/       : Performance metrics"
        echo "  - output/failures/         : Error logs (if any)"
    else
        print_warning "Sample data not found. Skipping analysis."
    fi
    
    echo ""
}

# Show next steps
show_next_steps() {
    echo ""
    echo "=================================================="
    echo "Setup Complete!"
    echo "=================================================="
    echo ""
    echo "Next Steps:"
    echo ""
    echo "1. View Spark Master UI:"
    echo "   Open http://localhost:8080 in your browser"
    echo ""
    echo "2. Run analysis on your own data:"
    echo "   - Copy your CSV/JSON file to data/input/"
    echo "   - Run: docker exec -it spark-master python3 -m src.main \\"
    echo "          --input /app/data/input/your_file.csv \\"
    echo "          --master spark://spark-master:7077 \\"
    echo "          --analysis full"
    echo ""
    echo "3. View results:"
    echo "   - Check output/ directory for results"
    echo "   - Graphs are in output/general/graphs/"
    echo ""
    echo "4. Use Makefile commands:"
    echo "   - make logs           : View cluster logs"
    echo "   - make status         : Check cluster status"
    echo "   - make shell          : Open shell in master"
    echo "   - make stop           : Stop the cluster"
    echo "   - make help           : Show all commands"
    echo ""
    echo "5. Scale workers:"
    echo "   docker-compose up -d --scale spark-worker-1=5"
    echo ""
    echo "=================================================="
}

# Main execution
main() {
    echo ""
    print_info "Starting quick start setup..."
    echo ""
    
    # Run setup steps
    check_prerequisites
    create_directories
    
    # Ask user if they want to generate sample data
    if command -v python3 &> /dev/null; then
        read -p "Generate sample data? (y/n) [y]: " generate_data
        generate_data=${generate_data:-y}
        if [ "$generate_data" = "y" ] || [ "$generate_data" = "Y" ]; then
            generate_sample_data
        fi
    fi
    
    # Ask user if they want to build images
    read -p "Build Docker images? (y/n) [y]: " build
    build=${build:-y}
    if [ "$build" = "y" ] || [ "$build" = "Y" ]; then
        build_images
    fi
    
    # Ask user if they want to start cluster
    read -p "Start Spark cluster? (y/n) [y]: " start
    start=${start:-y}
    if [ "$start" = "y" ] || [ "$start" = "Y" ]; then
        start_cluster
        
        # Ask user if they want to run sample analysis
        if [ -f "data/input/sample_sales.csv" ]; then
            read -p "Run sample analysis? (y/n) [y]: " run_analysis
            run_analysis=${run_analysis:-y}
            if [ "$run_analysis" = "y" ] || [ "$run_analysis" = "Y" ]; then
                run_sample_analysis
            fi
        fi
    fi
    
    show_next_steps
}

# Run main function
main
