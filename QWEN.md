# PVControl+ Project Documentation

## Project Overview

PVControl+ is a comprehensive solar photovoltaic (PV) energy monitoring and control system designed primarily for Raspberry Pi platforms. It provides real-time monitoring, data logging, and intelligent control of solar installations including battery charging systems, inverters, and load management.

The system is built using Python and integrates with various hardware components including sensors, relays, and communication protocols (I2C, Modbus, MQTT) to monitor and control solar installations. It features a web interface for visualization and configuration, backed by a MariaDB database for data persistence.

## Key Features

- Real-time monitoring of solar panel output, battery voltage/current, and power consumption
- Intelligent battery charging control with multiple modes (Bulk, Absorption, Float, Equalization)
- Relay control for load management and excess energy utilization
- Support for various inverter brands (Victron, GoodWe, Growatt, SMA, etc.)
- Web-based dashboard for monitoring and configuration
- Data logging and historical analysis capabilities
- Integration with MQTT for remote monitoring
- Telegram bot notifications
- Support for various sensor types and communication protocols (Modbus, RS485, etc.)

## Architecture

### Core Components

1. **Main Controller (`fv.py`)**: The central program that handles sensor readings, control algorithms, and data logging
2. **Database Layer**: MariaDB-based storage for historical data, configurations, and logs
3. **Web Interface**: PHP-based dashboard for monitoring and configuration
4. **Service Management**: systemd services for running components as background processes
5. **Configuration System**: Parameter files for customizing system behavior

### Hardware Integration

- GPIO control for relay switching
- I2C communication for sensor reading
- Modbus RTU/TCP for inverter communication
- MQTT for distributed system communication
- Various sensor interfaces (temperature, voltage, current)

## Refactored Architecture

The project is undergoing a refactoring effort to improve modularity and maintainability. The new architecture includes:

### Services (`servicios/` folder)
- New modular service implementations replacing older scripts
- Examples: `fv_ads.py`, `fv_rs485.py`, `fv_srne.py`

### Helpers (`helpers/` folder)
- **`control_procesos.py`**: Manages multiprocessing for concurrent device handling
- **`control_servicio.py`**: Controls service execution based on configuration
- **`gestor_bd.py`**: Database management layer
- **`gestor_logs.py`**: Logging management with configurable levels
- **`gestor_mqtt.py`**: MQTT communication abstraction
- **`gestor_parametros.py`**: Parameter loading with hot-reload capability
- **`gestor_telegram.py`**: Telegram bot integration

## Building and Running

### Prerequisites

- Raspberry Pi (recommended) or compatible Linux system
- Python 3.x
- MariaDB/MySQL database server
- Apache web server
- Various Python libraries (see `requirements.txt`)

### Installation

The project provides automated installation through the `PVControl+_Instalacion.py` script:

```bash
# Clone and install the complete system
sudo python3 PVControl+_Instalacion.py -c

# Or install only components without cloning
sudo python3 PVControl+_Instalacion.py
```

### Configuration

1. Run the initial configuration wizard:
```bash
python3 PVControl_Configuracion_Inicial.py
```

2. Configure your installation parameters in `Parametros_FV.py`

3. Start the services:
```bash
python3 Arrancar_servicios_PVControl+.py
```

### Service Management

- Start services: `python3 Arrancar_servicios_PVControl+.py`
- Stop services: `python3 Parar_Servicios_PVControl+.py`
- View running processes: `bash Ver_Programas_en_Ejecucion_PVControl+.sh`

## Development Conventions

### Code Structure

- Main logic is in `fv.py`
- Sensor drivers are in individual files (e.g., `victron.py`, `goodwe.py`, `fronius.py`)
- Web interface files are in the `html/` directory
- Configuration files are typically named `Parametros_FV*.py`
- Service files in `etc/systemd/system/` for systemd integration

### Configuration Files

- `Parametros_FV.py`: Main configuration file for the installation
- `Parametros_FV_DIST.py`: Distribution template with default values
- Service files in `etc/systemd/system/` for systemd integration

### Database Schema

The system uses MariaDB with tables for:
- `datos`: Main data logging table
- `reles`: Relay control configuration
- `parametros`: System parameters and control settings
- `log`: Event logging
- `diario`: Daily aggregated statistics

## Technology Stack

- **Backend**: Python 3.x
- **Database**: MariaDB/MySQL
- **Web Interface**: PHP
- **Web Server**: Apache
- **Communication Protocols**: MQTT, Modbus, I2C, RS485
- **Hardware Platform**: Raspberry Pi (primary target)
- **Service Management**: systemd

## Key Python Libraries Used

- `paho-mqtt`: MQTT communication
- `MySQLdb`: Database connectivity
- `minimalmodbus`: Modbus RTU communication
- `pymodbus`: Modbus TCP communication
- `gpiozero`: GPIO control
- `smbus`: I2C communication
- `telebot`: Telegram bot integration
- `Flask`: Web framework (in some components)

## File Organization

- `app/`: Application-specific code
- `html/`: Web interface files
- `servicios/`: Refactored service modules
- `helpers/`: Helper utilities and managers
- `params/`: Parameter templates
- `Manuales/`: Documentation
- `GIF/`: Visual aids
- `util/`: Utility scripts

## Common Tasks

### Adding New Device Support

New devices (inverters, charge controllers, etc.) can be added by creating new driver files similar to existing ones (e.g., `victron.py`, `goodwe.py`) and integrating them into the main system.

### Customizing Control Logic

Control algorithms can be customized through:
- Conditions in the `condiciones` table
- Parameters in `Parametros_FV.py`
- Custom relay control logic

### Extending Web Interface

The web interface can be customized by modifying PHP files in the `html/` directory, with different configurations available for different system types (with batteries, without batteries, etc.).

## Troubleshooting

- Check service status: `systemctl status fv.service`
- Review logs in the database `log` table
- Monitor system with: `python3 fv.py -p` for debug output
- Verify database connectivity and permissions