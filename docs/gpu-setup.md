# GPU Monitoring Setup for Devcontainer

The Salad Monitor service supports monitoring of CPU and GPU resources, including NVIDIA GPUs via `nvidia-smi`. When developing in the devcontainer, you'll need to set up access to GPU monitoring tools through host mounting or GPU passthrough.

## Option 1: Host Mounting (Recommended for Development)

To access GPU monitoring tools from your development environment:

1. Mount the host's NVIDIA libraries and tools into the container:
```json
{
    "mounts": [
        {
            "source": "/usr/lib/x86_64-linux-gnu/nvidia",
            "target": "/usr/lib/x86_64-linux-gnu/nvidia",
            "type": "bind"
        },
        {
            "source": "/usr/bin/nvidia-smi",
            "target": "/usr/bin/nvidia-smi",
            "type": "bind"
        }
    ]
}
```

2. Ensure the necessary libraries are available in your container:
```bash
# In your devcontainer, install required dependencies
sudo apt-get update && sudo apt-get install -y libnvidia-ml1
```

## Option 2: GPU Passthrough

For full GPU access, configure your container runtime to pass through GPU devices:

### With Docker:
```bash
docker run --gpus all your-devcontainer-image
```

### With Podman:
```bash
podman run --device=/dev/nvidia0:/dev/nvidia0 your-devcontainer-image
```

## Testing GPU Access

Once configured, verify GPU access in your devcontainer:
```bash
nvidia-smi
```

This will show information about available GPUs and their usage.