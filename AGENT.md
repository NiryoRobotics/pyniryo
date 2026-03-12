# AGENT.md - PyNiryo Project Guide

## Project Overview

**PyNiryo** is a Python SDK for controlling Niryo robots. It provides two distinct APIs:

1. **Ned API** (`pyniryo/ned/`) - Legacy TCP-based API for Niryo Ned/One robots
2. **Nate API** (`pyniryo/nate/`) - Modern HTTP + MQTT API for the upcoming Nate robot (pre-release)

- **License**: GNU General Public License v3.0
- **Current Version**: 1.2.3 (see `pyniryo/version.py`)
- **Python Support**: 3.10, 3.11, 3.12, 3.13
- **Repository**: 
  - GitLab (primary): https://gitlab.tools.niryo.com/robot/common/pyniryo.git
  - GitHub (mirror): https://github.com/NiryoRobotics/pyniryo.git

## Development Environment

### Virtual Environment

**Important**: This project uses a Python virtual environment. **All Python commands must be run within the activated virtual environment.**

**Location**: `venv/` (in the project root)

**Activation**:
```bash
# Linux/macOS (bash/zsh)
source venv/bin/activate

# Windows (cmd)
venv\Scripts\activate.bat

# Windows (PowerShell)
venv\Scripts\Activate.ps1
```

**Setup** (if not already created):
```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .[dev]
```

**Verification**:
```bash
# Verify you're in the virtual environment
which python  # Should show venv/bin/python
```

---

## Architecture

### Ned API (Legacy)

**Location**: `pyniryo/ned/`

- **Communication**: Direct TCP connection to robot
- **Main Class**: `NiryoRobot` in `pyniryo/ned/api/tcp_client.py`
- **Pattern**: Monolithic class with all robot control methods
- **Port**: Defined in `TCP_PORT` constant
- **Protocol**: Custom dict-based packet protocol (see `communication_functions.py`)

**Key Components**:
- `tcp_client.py` - Main client implementation (~3000+ lines)
- `objects.py` - Data objects (PoseObject, JointsPosition, etc.)
- `enums_communication.py` - Enums for commands, modes, pins, etc.
- `communication_functions.py` - Low-level packet encoding/decoding
- `exceptions.py` - Ned-specific exceptions

**Features**: Movement, calibration, I/O, tools, conveyors, vision, workspaces, frames, trajectories, LED ring, sound

---

### Nate API (Modern)

**Location**: `pyniryo/nate/`

The Nate API follows a **component-based architecture** with clean separation of concerns.

#### Client Entry Point

**File**: `pyniryo/nate/client.py`

```python
from pyniryo.nate.client import Nate

nate = Nate(hostname="10.10.10.10", login=("user", "password"))
# Or use environment variables: NATE_HOSTNAME, NATE_USERNAME, NATE_PASSWORD
```

The `Nate` class orchestrates:
- HTTP client for REST API calls
- MQTT client for real-time communication
- Token-based authentication with automatic renewal
- Component initialization

**Components** (accessed as properties on `Nate`):
- `nate.auth` - Authentication & token management
- `nate.users` - User management
- `nate.robot` - Robot control (movement, jogging, frames)
- `nate.device` - Device information
- `nate.programs` - Program execution and management
- `nate.motion_planner` - Trajectory generation
- `nate.metrics` - Custom metrics publishing
- `nate.io` - Digital/Analog I/O control

#### Communication Layer

**HTTP Client** (`pyniryo/nate/_internal/http.py`):
- Built on `requests` library
- Pydantic model validation for requests/responses
- Automatic error handling (ClientError, ServerError)
- Bearer token authentication
- SSL/TLS support (with insecure mode option)

**MQTT Client** (`pyniryo/nate/_internal/mqtt.py`):
- Built on `paho-mqtt` (MQTTv5)
- Topic subscriptions with typed callbacks
- QoS levels support
- Automatic reconnection on token renewal
- Topic prefix support (device-scoped: `device/{device_id}/...`)

#### Transport Model Pattern

**Critical Pattern**: All data transfer uses a **transport model abstraction**:

```
External API (models/) ←→ Transport Layer (_internal/transport_models/) ←→ HTTP/MQTT
```

**Public Models** (`pyniryo/nate/models/`):
- User-facing API (e.g., `Joints`, `Pose`, `Waypoint`)
- Provide `from_transport_model()` and `to_transport_model()` methods
- Clean, typed interfaces

**Transport Models** (`pyniryo/nate/_internal/transport_models/`):
- `models_gen.py` - Generated from OpenAPI specs (synchronous operations)
- `async_models_gen.py` - Generated from AsyncAPI specs (MQTT messages)
- `models.py` - Manual additions/overrides
- Raw Pydantic v2 models

**Example**:
```python
# Public model
joints = Joints(0.0, 0.1, 0.2, 0.3, 0.4, 0.5)

# Convert to transport model for API call
transport_joints = joints.to_transport_model()  # transport_models.s.Joints

# Convert back from API response
joints = Joints.from_transport_model(transport_joints)
```

#### Components Architecture

**Base Class** (`pyniryo/nate/components/base_api_component.py`):

All components inherit from `BaseAPIComponent`:
- Access to `self._http_client` (HttpClient)
- Access to `self._mqtt_client` (MqttClient)
- Access to `self._correlation_id` (for tracing)
- `close()` method for cleanup

**Example Component** (`pyniryo/nate/components/robot.py`):
- Synchronous operations via HTTP (e.g., `get_joints()`)
- Asynchronous subscriptions via MQTT (e.g., `on_joints(callback)`)
- Special classes for async operations (e.g., `MoveCommand`)

#### Code Generation

**Generated Files**:
1. `_internal/paths_gen.py` - API endpoint paths grouped by tags
2. `_internal/topics_gen.py` - MQTT topic constants
3. `_internal/transport_models/models_gen.py` - OpenAPI models
4. `_internal/transport_models/async_models_gen.py` - AsyncAPI models

**Generation Process**:

```bash
# Requires API specs from separate repository
make gen SPECS_DIR=/home/niryo/git/apid/doc
```

**Scripts**:
- `scripts/generate_paths.py` - Parses OpenAPI YAML, generates `StrEnum` classes for paths
- `scripts/generate_topics.py` - Parses AsyncAPI YAML, generates MQTT topic constants
- `scripts/generate_asyncapi_models.py` - Custom AsyncAPI → Pydantic generator (handles $ref resolution)

**Note**: OpenAPI models use `datamodel-codegen` (external tool), AsyncAPI models use custom script.

---

## Directory Structure

```
pyniryo/
├── __init__.py                 # Main entry point, exports public APIs
├── version.py                  # Version string
├── nate/                       # Nate API (modern)
│   ├── __init__.py
│   ├── client.py              # Nate client class
│   ├── exceptions.py          # Nate-specific exceptions
│   ├── _internal/             # Internal implementation (not for users)
│   │   ├── const.py           # Constants (ports, etc.)
│   │   ├── http.py            # HTTP client
│   │   ├── mqtt.py            # MQTT client
│   │   ├── paths_gen.py       # Generated: API paths
│   │   ├── topics_gen.py      # Generated: MQTT topics
│   │   └── transport_models/  # Generated: Pydantic models
│   │       ├── models_gen.py         # From OpenAPI
│   │       ├── async_models_gen.py   # From AsyncAPI
│   │       └── models.py             # Manual additions
│   ├── components/            # API components
│   │   ├── base_api_component.py
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── robot.py
│   │   ├── device.py
│   │   ├── programs.py
│   │   ├── motion_planner.py
│   │   ├── metrics.py
│   │   └── io.py
│   └── models/                # Public models
│       ├── auth.py
│       ├── geometry.py        # Joints, Pose, Point, Quaternion, EulerAngles
│       ├── motion.py          # Waypoint, Trajectory, Planner, MoveState
│       ├── robot.py           # RobotConfiguration, ControlMode, ExecutorStatus
│       ├── programs.py        # Program, ProgramExecution
│       ├── metrics.py         # Metric
│       └── io.py              # DigitalIO, AnalogIO
├── ned/                       # Ned API (legacy)
│   ├── __init__.py
│   └── api/
│       ├── tcp_client.py      # NiryoRobot class
│       ├── objects.py
│       ├── enums_communication.py
│       ├── communication_functions.py
│       └── exceptions.py
├── utils/                     # Shared utilities
└── vision/                    # Vision processing utilities

tests/
├── nate/                      # Nate API tests (unit tests with mocks)
│   ├── base.py               # BaseTestComponent with mocked clients
│   ├── test_auth.py
│   ├── test_robot.py
│   └── ...
└── ned/                       # Ned API tests (more integration-focused)
    ├── 01_main_purpose.py
    └── ...

examples/
├── nate/                      # Nate API examples
│   ├── move_joints.py
│   ├── move_poses.py
│   └── ...
└── ned/                       # Ned API examples
    └── simple_scripts/

scripts/
├── generate_paths.py          # OpenAPI → paths enum generator
├── generate_topics.py         # AsyncAPI → topics enum generator
├── generate_asyncapi_models.py # AsyncAPI → Pydantic models generator
├── build_docs_dev.py          # Development docs builder
└── build_docs_versioned.py    # Versioned docs builder

docs/                          # Sphinx documentation
```

---

## Key Development Patterns

### 1. Type Safety is Paramount

- Heavy use of type hints throughout the codebase
- Pydantic v2 models for all data structures
- Use `mypy` for type checking (listed in dev dependencies)
- All transport model conversions are type-safe

### 2. Transport Model Conversions

Always implement these methods in public models:

```python
@classmethod
def from_transport_model(cls, model: transport_models.s.SomeModel) -> 'PublicModel':
    """Convert from internal transport model to public model."""
    return cls(...)

def to_transport_model(self) -> transport_models.s.SomeModel:
    """Convert from public model to internal transport model."""
    return transport_models.s.SomeModel(...)
```

For MQTT models, sometimes there's also `from_a_transport_model()` for async variants.

### 3. Component Methods

Synchronous HTTP operations:
```python
def get_something(self) -> ReturnType:
    response = self._http_client.get(paths_gen.Component.GET_SOMETHING, 
                                     transport_models.s.Response)
    return ReturnType.from_transport_model(response)
```

Asynchronous MQTT subscriptions:
```python
def on_something(self, callback: Callable[[DataType], None]) -> None:
    def internal_callback(_, payload: transport_models.a.Payload) -> None:
        callback(DataType.from_transport_model(payload))
    
    self._mqtt_client.subscribe(topics_gen.Component.SOMETHING,
                               internal_callback,
                               transport_models.a.Payload)
```

Publishing MQTT commands:
```python
def command_something(self, data: DataType) -> None:
    self._mqtt_client.publish(topics_gen.Cmd.SOMETHING,
                             data.to_transport_model())
```

### 4. Async Command Tracking

For long-running operations (moves, program execution), use a command tracking pattern:

```python
class MoveCommand:
    """Tracks execution of a move command."""
    
    def __init__(self, mqtt_client: MqttClient, command_id: str):
        self.__mqtt_client = mqtt_client
        self.__command_id = command_id
        self.__feedbacks: List[MoveFeedback] = []
        
        # Subscribe to feedback
        self._mqtt_client.subscribe(self.topic, self.__callback, FeedbackModel)
    
    def wait(self, timeout: float = -1) -> None:
        """Wait for command completion."""
        # Poll state until final
        
    @property
    def state(self) -> MoveState:
        """Get current command state."""
        return self.__feedbacks[-1].state
```

### 5. Error Handling

Use specific exception types:
- `PyNiryoError` - Base exception
- `ApiError` - HTTP errors (base)
  - `ClientError` - 4xx errors
  - `ServerError` - 5xx errors
- `InternalError` - Internal SDK errors
- `DataValidationError` - Validation failures
- Operation-specific: `GenerateTrajectoryError`, `LoadTrajectoryError`, `ExecuteTrajectoryError`

---

## Testing

### Running Tests

```bash
# Run all tests
tox run-parallel --parallel auto

# Or directly with pytest
pytest tests/nate/
pytest tests/ned/
```

### Test Structure

**Nate Tests** (`tests/nate/`):
- Unit tests with mocked HTTP/MQTT clients
- Base class: `BaseTestComponent` provides mocked clients
- Pattern: Mock responses, call method, assert HTTP/MQTT calls

Example:
```python
from tests.nate.base import BaseTestComponent

class TestRobot(BaseTestComponent):
    def setUp(self):
        super().setUp()
        self.robot = Robot(http_client=self.http_client,
                          mqtt_client=self.mqtt_client,
                          correlation_id=self.correlation_id)
    
    def test_get_joints(self):
        # Mock response
        self.http_client.get.return_value = transport_models.s.Joints(...)
        
        # Call method
        joints = self.robot.get_joints()
        
        # Assert
        self.http_client.get.assert_called_once_with(...)
        self.assertIsInstance(joints, geometry.Joints)
```

**Ned Tests** (`tests/ned/`):
- More integration-focused (numbered sequence)
- Typically require a real robot or manual review

### No Integration Tests Yet

Currently, there are no automated integration tests against a real Nate robot. All tests use mocks.

---

## Branching Strategy & Releases

### Current Branch Structure

- **`master-nate`** - Active development branch for Nate API
  - Nate robot is not yet publicly released
  - Working branch for all Nate-related development
- **`master`** - Stable branch (currently Ned-focused)
  - Will merge `master-nate` when Nate is officially released

### Version Scheme

- **Ned API**: Version 1.x.x (stable, released)
- **Nate API**: Version 0.x.x (pre-release, major=0 indicates pre-release status)
- Version defined in `pyniryo/version.py`

### Release Process (from `.gitlab-ci.yml`)

1. **On tag push** to `master` branch:
   - Build package → `dist/`
   - Upload to PyPI
   - Build Docker images (multi-arch: amd64, arm64)
   - Mirror to GitHub
   
2. **On `master-nate` branch**:
   - Run tests
   - Build Docker images (dev/staging)

---

## Dependencies

### Core Runtime

From `requirements.txt`:

**Ned API**:
- `enum34` - Enum backport
- `opencv-python` - Computer vision
- `numpy` - Numerical operations
- `typing-extensions` - Type hint extensions

**Nate API**:
- `paho-mqtt` - MQTT client
- `requests` - HTTP client
- `types-requests` - Type stubs for requests
- `pydantic` - Data validation
- `pydantic[email]` - Email validation support
- `strenum` - String enums

### Development

From `requirements.txt` extras:

**Tests** (`[tests]`):
- `pytest` - Test framework
- `coverage` - Code coverage
- `tox` - Test automation

**Documentation** (`[docs]`):
- Sphinx and related packages
- See `docs/requirements.txt`

**Code Generation** (`[scripts]`):
- `datamodel-codegen` - OpenAPI to Pydantic
- `jinja2` - Template engine
- `pyyaml` - YAML parsing
- See `scripts/requirements.txt`

**Development** (`[dev]`):
- All of the above
- `mypy` - Type checking

---

## Environment Variables

### Nate Client Configuration

The `Nate` class reads these environment variables:

**Authentication**:
- `NATE_HOSTNAME` - Robot hostname/IP (default: `localhost`)
- `NATE_USERNAME` - Username for authentication
- `NATE_PASSWORD` - Password for authentication
- `NATE_TOKEN` - Direct token (bypasses username/password)

**Advanced Options** (not in constructor):
- `NATE_HTTP_PORT` - HTTP API port (default: 8443)
- `NATE_MQTT_PORT` - MQTT broker port (default: 1883)
- `NATE_INSECURE` - Disable SSL verification (any value = enabled)
- `NATE_USE_HTTP` - Use HTTP instead of HTTPS (any value = enabled)
- `NATE_EXECUTION_TOKEN` - Execution token header
- `NATE_TOKEN_VALIDITY` - Token validity duration (e.g., "1d", "12h", "3600s")
- `NATE_CORRELATION_ID` - Correlation ID for tracing

---

## Common Operations

### Code Generation Workflow

When API specs change:

```bash
# 1. Get latest specs (from apid repository)
cd /home/niryo/git/apid
git pull

# 2. Generate code in pyniryo
cd /home/niryo/git/pyniryo
make gen SPECS_DIR=/home/niryo/git/apid/doc

# 3. Review generated files
git diff pyniryo/nate/_internal/
```

**Generated Files** (do not edit manually):
- `pyniryo/nate/_internal/paths_gen.py`
- `pyniryo/nate/_internal/topics_gen.py`
- `pyniryo/nate/_internal/transport_models/models_gen.py`
- `pyniryo/nate/_internal/transport_models/async_models_gen.py`

### Adding a New Component

1. Create component class in `pyniryo/nate/components/new_component.py`:

```python
from .base_api_component import BaseAPIComponent
from .._internal import transport_models, paths_gen, topics_gen
from ..models.new_models import PublicModel

class NewComponent(BaseAPIComponent):
    def get_something(self) -> PublicModel:
        response = self._http_client.get(
            paths_gen.NewComponent.GET_SOMETHING,
            transport_models.s.Response
        )
        return PublicModel.from_transport_model(response)
```

2. Create public models in `pyniryo/nate/models/new_models.py`

3. Add to `pyniryo/nate/components/__init__.py`:

```python
from .new_component import NewComponent

__all__ = [..., 'NewComponent']
```

4. Add to `Nate` client in `pyniryo/nate/client.py`:

```python
class Nate:
    new_component: NewComponent
    
    def __init__(self, ...):
        ...
        self.new_component = NewComponent(self._http_client, 
                                          self._mqtt_client,
                                          self._correlation_id)
    
    def close(self):
        ...
        self.new_component.close()
```

5. Write tests in `tests/nate/test_new_component.py`

### Adding a New Public Model

1. Check if transport model exists in generated files
2. Create public model in appropriate `pyniryo/nate/models/*.py`:

```python
from dataclasses import dataclass
from .._internal import transport_models

@dataclass
class NewModel:
    field1: str
    field2: int
    
    @classmethod
    def from_transport_model(cls, model: transport_models.s.NewModel) -> 'NewModel':
        return cls(
            field1=model.field1,
            field2=model.field2
        )
    
    def to_transport_model(self) -> transport_models.s.NewModel:
        return transport_models.s.NewModel(
            field1=self.field1,
            field2=self.field2
        )
```

---

## Important Files Reference

### Entry Points
- `pyniryo/__init__.py` - Main package entry, exports `NiryoRobot`, `Nate`, and common types
- `pyniryo/nate/client.py` - Nate client implementation
- `pyniryo/ned/api/tcp_client.py` - Ned client implementation

### Configuration
- `setup.py` - Package metadata and dependencies
- `pyproject.toml` - Build system configuration
- `requirements.txt` - Runtime dependencies
- `pyniryo/version.py` - Version string
- `.gitlab-ci.yml` - CI/CD pipeline

### Code Generation
- `Makefile` - Build automation (especially `gen` target)
- `scripts/generate_paths.py` - Generate API path enums
- `scripts/generate_topics.py` - Generate MQTT topic constants
- `scripts/generate_asyncapi_models.py` - Generate AsyncAPI Pydantic models

### Testing
- `tests/nate/base.py` - Base test class with mocked clients
- `tox.ini` - Test automation configuration
- `.coveragerc` - Coverage configuration

### Documentation
- `README.rst` - Project overview and quick start
- `docs/` - Sphinx documentation source
- `docs/api/nate/api.rst` - Nate API documentation
- `docs/api/ned/api.rst` - Ned API documentation

---

## API Design Philosophy

### Nate API Design Principles

1. **Type Safety**: Everything is typed, validated with Pydantic
2. **Separation of Concerns**: Components handle specific domains
3. **Async/Sync Split**: HTTP for commands, MQTT for streaming/events
4. **Transport Abstraction**: Public API decoupled from wire format
5. **Testability**: Easy to mock HTTP/MQTT for unit tests
6. **Resource Management**: Context managers for cleanup
7. **Progressive Disclosure**: Simple cases are simple, complex cases possible

### Ned API Design

- **Monolithic**: All methods on single `NiryoRobot` class
- **Stateful**: Maintains TCP connection
- **Synchronous**: Blocking operations
- **Backward Compatible**: Stable API, deprecated methods marked

---

## Common Gotchas

1. **Generated Code**: Don't edit `*_gen.py` files - they'll be overwritten
2. **Transport Models**: Always use `from_transport_model()`/`to_transport_model()` - don't construct transport models directly in public API
3. **MQTT Topics**: Include device prefix when needed (handled by `MqttClient`)
4. **Token Renewal**: Automatic in `Nate` client via `TokenRenewer`
5. **Resource Cleanup**: Always call `nate.close()` or use context manager
6. **Type Checking**: Run `mypy` to catch type errors early

---

## Future Considerations

### When Nate is Released

1. Merge `master-nate` → `master`
2. Bump Nate version to 1.0.0 (remove pre-release major=0)
3. Update documentation to promote Nate as primary API
4. Consider integration tests

### Potential Improvements

- Integration test framework for Nate
- Async/await support (currently sync only)
- Connection pooling for HTTP
- Better offline behavior
- Performance optimizations

---

## Quick Reference Commands

```bash
# Setup development environment
python3 -m venv venv
source venv/bin/activate
pip install -e .[dev]

# Generate code from API specs
make gen SPECS_DIR=/home/niryo/git/apid/doc

# Run tests
tox run-parallel --parallel auto
# or
pytest tests/nate/

# Type checking
mypy pyniryo/nate/

# Build documentation
cd docs
make html

# Build package
python3 -m build

# Install from source
pip install -e .

# Run examples
python examples/nate/basic_move.py
```

---

## Contact & Resources

- **GitLab**: https://gitlab.tools.niryo.com/robot/common/pyniryo.git
- **GitHub**: https://github.com/NiryoRobotics/pyniryo.git
- **Documentation**: https://niryorobotics.github.io/pyniryo
- **PyPI**: https://pypi.org/project/pyniryo/

---

**Last Updated**: 2026-03-02  
**AI Agent Note**: This document is specifically designed to help AI coding assistants understand the PyNiryo project structure, patterns, and conventions.
