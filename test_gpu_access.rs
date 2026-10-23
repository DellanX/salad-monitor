use nvml_wrapper::Nvml;
use std::error::Error;

fn main() -> Result<(), Box<dyn Error>> {
    println!("Testing GPU access with NVML...");
    
    // Initialize NVML
    let nvml = Nvml::init()?;
    println!("NVML initialized successfully!");
    
    // Get the number of GPUs
    let device_count = nvml.device_count()?;
    println!("Number of GPUs found: {}", device_count);
    
    if device_count > 0 {
        // Try to get information about the first GPU
        let device = nvml.device_by_index(0)?;
        let name = device.name()?;
        println!("GPU 0 name: {}", name);
        
        let pci_info = device.pci_info()?;
        println!("PCI Bus ID: {}", pci_info.bus_id);
        
        // Get memory info
        let mem_info = device.memory_info()?;
        println!("Memory Info - Total: {} MB, Free: {} MB, Used: {} MB", 
                 mem_info.total / 1024 / 1024,
                 mem_info.free / 1024 / 1024,
                 mem_info.used / 1024 / 1024);
        
        println!("GPU access test completed successfully!");
    } else {
        println!("No GPUs found");
    }
    
    Ok(())
}