# Trash Detection System - Modular Structure

This document describes the new modular structure of the trash detection system, which has been refactored from a single monolithic file into organized, reusable components.

## Directory Structure

```
streetsweep/
├── src/
│   └── trash_detector/
│       ├── __init__.py                 # Package initialization
│       ├── config.py                   # Configuration and constants
│       ├── detector.py                 # Main TrashDetector class
│       ├── models/
│       │   ├── __init__.py
│       │   └── yolo_model.py          # YOLO model handler
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── image_utils.py         # Image processing utilities
│       │   └── detection_filters.py   # Detection filtering logic
│       └── collection/
│           ├── __init__.py
│           └── trash_collector.py     # Collection management system
├── main.py                            # New main entry point
├── collection_manager.py              # CLI tool for collection data
├── trash_detector.py                  # Original monolithic file (kept for reference)
└── requirements.txt
```

## Key Components

### 1. Configuration (`config.py`)

- Centralized configuration and constants
- Trash class definitions
- Detection filtering parameters
- Default values for models and thresholds

### 2. Main Detector (`detector.py`)

- Simplified TrashDetector class
- Focuses on high-level detection workflow
- Integrates with YOLO model and utilities

### 3. YOLO Model (`models/yolo_model.py`)

- Encapsulates all YOLO-specific logic
- Handles model loading and inference
- Manages rotation-based detection
- Processes detection results

### 4. Image Utilities (`utils/image_utils.py`)

- Image rotation and coordinate transformation
- IoU calculation and duplicate removal
- Detection visualization
- Camera enumeration

### 5. Detection Filters (`utils/detection_filters.py`)

- Size and confidence-based filtering
- Class-specific filtering rules
- Trash likelihood assessment

### 6. Collection System (`collection/trash_collector.py`)

- Session management
- Data persistence
- Statistics and reporting
- Export functionality

## Usage

### Basic Detection

```bash
# Use the new main entry point
python main.py --source 1

# List available cameras
python main.py --list-cameras

# Test mode
python main.py --test
```

### Collection Mode

```bash
# Enable collection tracking
python main.py --source 1 --collection-mode --location "Park Area A"

# With verbose logging
python main.py --source 1 --collection-mode --verbose
```

### Collection Management

```bash
# List all collection sessions
python collection_manager.py list

# Show session details
python collection_manager.py show session_1234567890

# Export session data
python collection_manager.py export session_1234567890 --format csv

# Show overall statistics
python collection_manager.py stats
```

## Key Improvements

### 1. **Modularity**

- Each component has a single responsibility
- Easy to test individual components
- Reusable across different applications

### 2. **Maintainability**

- Clear separation of concerns
- Easier to modify specific functionality
- Better code organization

### 3. **Extensibility**

- Easy to add new detection models
- Simple to extend collection features
- Plugin-like architecture for utilities

### 4. **Data Management**

- Persistent collection sessions
- Export capabilities (JSON, CSV)
- Statistical analysis tools

### 5. **Configuration**

- Centralized configuration
- Easy to adjust detection parameters
- Environment-specific settings

## Migration from Original

The original `trash_detector.py` file is preserved for reference. The new modular system provides:

- **Same functionality** with better organization
- **Enhanced features** like collection tracking
- **Better maintainability** through separation of concerns
- **Improved extensibility** for future enhancements

## Development

### Adding New Features

1. **New Detection Models**: Add to `models/` directory
2. **New Utilities**: Add to `utils/` directory
3. **New Collection Features**: Extend `collection/` modules
4. **Configuration Changes**: Update `config.py`

### Testing

```bash
# Test individual components
python -c "from src.trash_detector import TrashDetector; print('Import successful')"

# Test collection system
python -c "from src.trash_detector import TrashCollector; c = TrashCollector(); print('Collection system ready')"
```

## Benefits

1. **Cleaner Code**: Each file has a focused purpose
2. **Better Testing**: Components can be tested in isolation
3. **Easier Debugging**: Issues can be traced to specific modules
4. **Team Development**: Multiple developers can work on different components
5. **Documentation**: Each module can have focused documentation
6. **Reusability**: Components can be used in other projects

This modular structure makes the trash detection system more professional, maintainable, and ready for production deployment.
