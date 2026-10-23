#!/bin/bash

echo "Testing GPU access in devcontainer..."

# Check if nvidia-smi is available
if command -v nvidia-smi &> /dev/null; then
    echo "nvidia-smi found:"
    nvidia-smi
else
    echo "nvidia-smi not found. This might be expected in the container."
fi

# Check for GPU libraries
echo "Checking for NVIDIA libraries..."
ldconfig -p | grep nvidia

echo "Testing NVML access with Rust test script..."
if [ -f "test_gpu_access.rs" ]; then
    echo "Rust test script found. Building and running..."
    # Try to compile and run the test
    rustc --edition=2021 test_gpu_access.rs -o test_gpu_access
    if [ $? -eq 0 ]; then
        echo "Compilation successful. Running test..."
        ./test_gpu_access
    else
        echo "Compilation failed, but that's okay for now."
    fi
else
    echo "No test script found."
fi

echo "GPU testing complete."