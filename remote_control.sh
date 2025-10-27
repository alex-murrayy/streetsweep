#!/bin/bash

# Remote Control Script for Raspberry Pi Trash Detection System
# Allows you to control the Pi system remotely via SSH

PI_USER="pi"
PI_HOST=""
PI_PATH="/home/pi/streetsweep"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Function to check if Pi host is set
check_pi_host() {
    if [ -z "$PI_HOST" ]; then
        print_error "PI_HOST not set. Please set the IP address of your Raspberry Pi."
        echo "Usage: export PI_HOST=192.168.1.100"
        echo "Or edit this script to set PI_HOST variable"
        exit 1
    fi
}

# Function to test SSH connection
test_connection() {
    print_status "Testing SSH connection to $PI_HOST..."
    if ssh -o ConnectTimeout=5 -o BatchMode=yes $PI_USER@$PI_HOST exit 2>/dev/null; then
        print_status "SSH connection successful"
        return 0
    else
        print_error "SSH connection failed"
        return 1
    fi
}

# Function to start mjpg-streamer
start_stream() {
    print_header "Starting Video Stream"
    check_pi_host
    
    if test_connection; then
        print_status "Starting mjpg-streamer on Pi..."
        ssh $PI_USER@$PI_HOST "sudo systemctl start mjpg-streamer"
        
        if [ $? -eq 0 ]; then
            print_status "Video stream started successfully"
            print_status "Access stream at: http://$PI_HOST:8080"
        else
            print_error "Failed to start video stream"
        fi
    fi
}

# Function to stop mjpg-streamer
stop_stream() {
    print_header "Stopping Video Stream"
    check_pi_host
    
    if test_connection; then
        print_status "Stopping mjpg-streamer on Pi..."
        ssh $PI_USER@$PI_HOST "sudo systemctl stop mjpg-streamer"
        print_status "Video stream stopped"
    fi
}

# Function to start trash detection
start_detection() {
    print_header "Starting Trash Detection"
    check_pi_host
    
    if test_connection; then
        print_status "Starting trash detection system on Pi..."
        ssh $PI_USER@$PI_HOST "cd $PI_PATH/imaging && ./start_trash_detection.sh"
    fi
}

# Function to stop trash detection
stop_detection() {
    print_header "Stopping Trash Detection"
    check_pi_host
    
    if test_connection; then
        print_status "Stopping trash detection system on Pi..."
        ssh $PI_USER@$PI_HOST "sudo systemctl stop trash-detection"
        print_status "Trash detection stopped"
    fi
}

# Function to test system
test_system() {
    print_header "Testing System"
    check_pi_host
    
    if test_connection; then
        print_status "Running system tests on Pi..."
        ssh $PI_USER@$PI_HOST "cd $PI_PATH && ./test_system.sh"
    fi
}

# Function to test camera
test_camera() {
    print_header "Testing Camera"
    check_pi_host
    
    if test_connection; then
        print_status "Testing camera on Pi..."
        ssh $PI_USER@$PI_HOST "cd $PI_PATH && ./test_camera.sh"
    fi
}

# Function to test Arduino
test_arduino() {
    print_header "Testing Arduino"
    check_pi_host
    
    if test_connection; then
        print_status "Testing Arduino on Pi..."
        ssh $PI_USER@$PI_HOST "cd $PI_PATH && ./test_arduino.sh"
    fi
}

# Function to view logs
view_logs() {
    print_header "Viewing Logs"
    check_pi_host
    
    if test_connection; then
        print_status "Showing recent logs..."
        ssh $PI_USER@$PI_HOST "journalctl -u trash-detection -f"
    fi
}

# Function to restart services
restart_services() {
    print_header "Restarting Services"
    check_pi_host
    
    if test_connection; then
        print_status "Restarting all services on Pi..."
        ssh $PI_USER@$PI_HOST "sudo systemctl restart mjpg-streamer trash-detection"
        print_status "Services restarted"
    fi
}

# Function to update code
update_code() {
    print_header "Updating Code"
    check_pi_host
    
    if test_connection; then
        print_status "Updating code on Pi..."
        ssh $PI_USER@$PI_HOST "cd $PI_PATH && git pull"
        print_status "Code updated"
    fi
}

# Function to show system status
show_status() {
    print_header "System Status"
    check_pi_host
    
    if test_connection; then
        print_status "Checking system status on Pi..."
        ssh $PI_USER@$PI_HOST "
            echo '=== Service Status ==='
            sudo systemctl status mjpg-streamer --no-pager -l
            echo ''
            sudo systemctl status trash-detection --no-pager -l
            echo ''
            echo '=== Camera Status ==='
            ls -la /dev/video*
            echo ''
            echo '=== Arduino Status ==='
            ls -la /dev/ttyUSB* /dev/ttyACM*
            echo ''
            echo '=== System Resources ==='
            free -h
            df -h /
            echo ''
            echo '=== Network Status ==='
            hostname -I
        "
    fi
}

# Function to open video stream in browser
open_stream() {
    check_pi_host
    print_status "Opening video stream in browser..."
    
    if command -v open >/dev/null 2>&1; then
        # macOS
        open "http://$PI_HOST:8080"
    elif command -v xdg-open >/dev/null 2>&1; then
        # Linux
        xdg-open "http://$PI_HOST:8080"
    else
        print_warning "Cannot auto-open browser. Please manually open: http://$PI_HOST:8080"
    fi
}

# Function to monitor system in real-time
monitor_system() {
    print_header "Real-time System Monitor"
    check_pi_host
    
    if test_connection; then
        print_status "Starting real-time monitoring..."
        ssh $PI_USER@$PI_HOST "
            while true; do
                clear
                echo '=== Trash Detection System Monitor ==='
                echo 'Time: \$(date)'
                echo ''
                echo '=== Services ==='
                sudo systemctl is-active mjpg-streamer trash-detection
                echo ''
                echo '=== Camera ==='
                ls -la /dev/video* 2>/dev/null || echo 'No cameras found'
                echo ''
                echo '=== Arduino ==='
                ls -la /dev/ttyUSB* /dev/ttyACM* 2>/dev/null || echo 'No Arduino found'
                echo ''
                echo '=== System Resources ==='
                free -h | head -2
                df -h / | tail -1
                echo ''
                echo '=== Network ==='
                hostname -I
                echo ''
                echo 'Press Ctrl+C to exit'
                sleep 5
            done
        "
    fi
}

# Function to show help
show_help() {
    echo "Remote Control Script for Trash Detection System"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start-stream     Start video stream on Pi"
    echo "  stop-stream      Stop video stream on Pi"
    echo "  start-detection  Start trash detection system"
    echo "  stop-detection   Stop trash detection system"
    echo "  test            Test entire system"
    echo "  test-camera     Test camera functionality"
    echo "  test-arduino    Test Arduino connection"
    echo "  logs            View system logs"
    echo "  restart         Restart all services"
    echo "  update          Update code from git"
    echo "  status          Show system status"
    echo "  open-stream     Open video stream in browser"
    echo "  monitor         Real-time system monitoring"
    echo "  help            Show this help message"
    echo ""
    echo "Setup:"
    echo "  export PI_HOST=192.168.1.100  # Set your Pi's IP address"
    echo "  ssh-copy-id $PI_USER@\$PI_HOST  # Set up SSH keys"
    echo ""
    echo "Examples:"
    echo "  $0 start-stream"
    echo "  $0 test"
    echo "  $0 status"
    echo "  $0 monitor"
}

# Main script logic
case "$1" in
    "start-stream")
        start_stream
        ;;
    "stop-stream")
        stop_stream
        ;;
    "start-detection")
        start_detection
        ;;
    "stop-detection")
        stop_detection
        ;;
    "test")
        test_system
        ;;
    "test-camera")
        test_camera
        ;;
    "test-arduino")
        test_arduino
        ;;
    "logs")
        view_logs
        ;;
    "restart")
        restart_services
        ;;
    "update")
        update_code
        ;;
    "status")
        show_status
        ;;
    "open-stream")
        open_stream
        ;;
    "monitor")
        monitor_system
        ;;
    "help"|"--help"|"-h"|"")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
