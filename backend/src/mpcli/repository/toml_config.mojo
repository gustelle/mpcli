// TOML configuration reader
// Equivalent to toml_config.py

from string import String
from list import List
from option import Optional

from ..entities.exceptions import AudioFileNotFoundError

fn read_configurations[T: Copyable](
    config_path: String,
    section_name: String,
    entity_type: Type[T],
) raises -> List[T]:
    """
    Read a TOML configuration file and return a list of entities of type T.
    
    Args:
        config_path: Path to the TOML configuration file.
        section_name: Name of the section in the TOML file.
        entity_type: Type of the entity to create from the configuration.
    
    Returns:
        List[T]: List of entities created from the configuration.
    
    Raises:
        AudioFileNotFoundError: If the config file cannot be read.
    """
    from python import Python
    from os.path import exists
    
    if not exists(config_path):
        raise AudioFileNotFoundError(f"Config file '{config_path}' not found")
    
    try:
        tomllib = Python.import_module("tomllib")
        
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
        
        let section = config[section_name]
        
        if Python.isinstance(section, list):
            // Handle list of configurations
            let result = List[T]()
            for item in section:
                result.append(entity_type(**item))
            return result
        else:
            // Handle single configuration
            let result = List[T]()
            result.append(entity_type(**section))
            return result
    except e:
        raise AudioFileNotFoundError(f"Error reading config file '{config_path}': {e}")
