# Phase 11.5-11.7: Industrial Dataset Curation & AI Control Optimization Framework

## Executive Summary

This framework defines a comprehensive system for ingesting, curating, and processing industrial control system datasets to train AI models for PID control optimization and hybrid Model Predictive Control (hMPC). The system will interface directly with PLCs via OPC-UA to provide real-time control optimization in production environments.

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Dataset Curation & AI Control System             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐          │
│  │   Dataset    │   │   Variable   │   │     AI       │          │
│  │  Ingestion   │──▶│Classification│──▶│  Supervisor  │          │
│  └──────────────┘   └──────────────┘   └──────────────┘          │
│         │                   │                    │                  │
│         ▼                   ▼                    ▼                  │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐          │
│  │   Metadata   │   │   Feature    │   │   Control    │          │
│  │  Management  │   │ Engineering  │   │ Optimization │          │
│  └──────────────┘   └──────────────┘   └──────────────┘          │
│                                                 │                   │
│                                                 ▼                   │
│                                    ┌───────────────────────┐       │
│                                    │   OPC-UA Interface    │       │
│                                    │   (Read/Write PLCs)   │       │
│                                    └───────────────────────┘       │
└─────────────────────────────────────────────────────────────────────┘
```

## 1. Dataset Structure & Variable Types

### 1.1 Core Variable Types (11 Types)

#### 1.1.1 Process Variables (PV)
```python
@dataclass
class ProcessVariable:
    """Process Variables directly affected by Control Variables"""
    tag_name: str
    value: float
    timestamp: datetime

    # Metadata
    is_primary_pv: bool  # PPV flag
    is_secondary_pv: bool  # SPC flag
    range_high: float
    range_low: float
    max_value: float  # For normalization: PV/PV_max
    engineering_unit: str
    quality_code: int  # OPC-UA quality

    def normalize(self) -> float:
        """Return normalized value [0, 1]"""
        return self.value / self.max_value if self.max_value > 0 else 0.0
```

#### 1.1.2 Control Variables (CV)
```python
@dataclass
class ControlVariable:
    """Control Variables - up to 2 per control process"""
    tag_name: str
    value: float
    timestamp: datetime

    # Metadata
    range_high: float
    range_low: float
    max_value: float  # For normalization: CV/CV_max
    engineering_unit: str
    rate_limit: float  # Max rate of change per minute
    is_primary_cv: bool
    actuator_type: str  # valve, pump, heater, etc.
```

#### 1.1.3 Disturbance Variables (DV)
```python
@dataclass
class DisturbanceVariable:
    """Variables not directly affected by CV but impact PVs"""
    tag_name: str
    value: float
    timestamp: datetime

    # Metadata
    range_high: float
    range_low: float
    max_value: float  # For normalization: DV/DV_max
    engineering_unit: str
    is_measured: bool  # True if measurable, False if estimated
    correlation_strength: Dict[str, float]  # Correlation with PVs
```

#### 1.1.4 Setpoint Variables (SP)
```python
@dataclass
class SetpointVariable:
    """Setpoint variables - multiple per dataset for optimization"""
    tag_name: str
    value: float
    timestamp: datetime

    # Metadata
    range_high: float
    range_low: float
    engineering_unit: str
    associated_pv: str  # Tag name of associated PV
    optimization_priority: int  # For multi-SP optimization
```

#### 1.1.5 Process State & Mode
```python
@dataclass
class ProcessState:
    """Current state and mode of the process"""
    timestamp: datetime
    state: str  # "startup", "steady_state", "shutdown", "transition"
    mode: str   # "manual", "auto", "cascade", "mpc"
    sub_state: Optional[str]  # Additional state details
    transition_trigger: Optional[str]  # What caused state change
```

#### 1.1.6 Controller Configuration
```python
@dataclass
class ControllerConfig:
    """Controller type and parameters"""
    timestamp: datetime
    controller_type: str  # "P", "PI", "PID", "SA", "MPC"
    pid_type: str  # "dependent", "independent"

    # PID Parameters (naming depends on pid_type)
    kc_or_kp: float  # Kc for dependent, Kp for independent
    ti_or_ki: float  # Ti for dependent, Ki for independent
    td_or_kd: float  # Td for dependent, Kd for independent

    # Additional parameters
    filter_time: float
    dead_band: float
    output_bias: float
```

### 1.2 Dataset Format Example

Based on the `data_beerfeed_03_02-05_09-2025.xls` format:
```python
@dataclass
class IndustrialDataset:
    """Container for a complete industrial dataset"""
    dataset_id: str
    process_name: str
    start_time: datetime
    end_time: datetime
    sample_rate: float  # seconds

    # Variable collections
    process_variables: List[ProcessVariable]
    control_variables: List[ControlVariable]
    disturbance_variables: List[DisturbanceVariable]
    setpoints: List[SetpointVariable]
    process_states: List[ProcessState]
    controller_configs: List[ControllerConfig]

    # Metadata
    data_quality_score: float
    completeness_score: float
    validated: bool
```

## 2. Dataset Ingestion & Curation Pipeline

### 2.1 Data Ingestion Module
```python
class DataIngestionPipeline:
    """Multi-format data ingestion system"""

    def ingest_csv_excel(self, file_path: Path) -> IndustrialDataset:
        """Import CSV/Excel files like data_beerfeed format"""
        # Implementation details...

    def ingest_opcua_stream(self, server_url: str) -> AsyncIterator[IndustrialDataset]:
        """Real-time OPC-UA data streaming"""
        # Implementation details...

    def ingest_historian(self, connection: HistorianConnection) -> IndustrialDataset:
        """Extract from industrial historians (InfluxDB, TimescaleDB)"""
        # Implementation details...
```

### 2.2 Data Validation & Quality
```python
class DataValidator:
    """Validate and assess data quality"""

    def validate_ranges(self, dataset: IndustrialDataset) -> ValidationReport:
        """Check all variables against defined ranges"""

    def detect_bad_data(self, dataset: IndustrialDataset) -> List[BadDataPoint]:
        """Identify outliers, frozen values, noise"""

    def assess_completeness(self, dataset: IndustrialDataset) -> float:
        """Calculate data completeness score"""
```

### 2.3 Time Synchronization
```python
class TimeSynchronizer:
    """Handle time alignment and resampling"""

    def align_timestamps(self, dataset: IndustrialDataset) -> IndustrialDataset:
        """Align all variables to common time base"""

    def resample(self, dataset: IndustrialDataset, target_rate: float) -> IndustrialDataset:
        """Resample to target sample rate"""
```

## 3. Feature Engineering & Augmentation

### 3.1 Derived Features
```python
class FeatureEngineer:
    """Generate additional features for AI models"""

    def calculate_derivatives(self, dataset: IndustrialDataset) -> Dict[str, np.ndarray]:
        """Calculate rate of change for all variables"""

    def calculate_integrals(self, dataset: IndustrialDataset) -> Dict[str, np.ndarray]:
        """Calculate accumulated values"""

    def moving_statistics(self, dataset: IndustrialDataset, windows: List[int]) -> Dict[str, np.ndarray]:
        """Moving averages, std dev, min/max"""

    def frequency_features(self, dataset: IndustrialDataset) -> Dict[str, np.ndarray]:
        """FFT-based features for oscillation detection"""

    def cross_correlations(self, dataset: IndustrialDataset) -> np.ndarray:
        """Cross-correlation matrix between variables"""
```

## 4. AI Supervisor Implementation

### 4.1 Goal 1: PID Control Optimization

#### 4.1.1 Classical Tuning Methods
```python
class PIDTuningMethods:
    """Implementation of classical PID tuning methods"""

    def ziegler_nichols_open_loop(self, step_response: StepResponse) -> PIDParameters:
        """Open-loop Ziegler-Nichols method"""
        L = step_response.dead_time
        T = step_response.time_constant
        K = step_response.process_gain

        # PI Controller
        Kc = 0.9 * T / (K * L)
        Ti = L / 0.3

        return PIDParameters(Kc=Kc, Ti=Ti, Td=0)

    def cohen_coon(self, step_response: StepResponse) -> PIDParameters:
        """Cohen-Coon method for processes with dead time"""
        # Implementation based on docs/basic_loop_tuning_methods.txt

    def imc_lambda(self, process_model: FOPDTModel, lambda_tc: float) -> PIDParameters:
        """IMC/Lambda tuning method"""
        # Implementation based on docs/Model Based Tuning.txt
```

#### 4.1.2 AI-Enhanced Tuning
```python
class AITuningOptimizer:
    """Machine learning enhanced PID tuning"""

    def __init__(self):
        self.model = self._build_neural_network()
        self.process_identifier = ProcessIdentifier()

    def optimize_pid(self, dataset: IndustrialDataset) -> PIDParameters:
        """Use ML to find optimal PID parameters"""
        # Extract process characteristics
        process_model = self.process_identifier.identify(dataset)

        # Feature vector: dead time, time constant, gain, noise level, etc.
        features = self._extract_features(process_model, dataset)

        # Predict optimal parameters
        optimal_params = self.model.predict(features)

        # Validate against stability margins
        return self._validate_stability(optimal_params, process_model)
```

### 4.2 Goal 2: Hybrid MPC Implementation

#### 4.2.1 Model Identification
```python
class MPCModelBuilder:
    """Build predictive models from data"""

    def identify_state_space(self, dataset: IndustrialDataset) -> StateSpaceModel:
        """Identify state-space model from data"""
        # System identification using subspace methods

    def identify_fopdt(self, dataset: IndustrialDataset) -> FOPDTModel:
        """Identify First Order Plus Dead Time model"""
        # Curve fitting to step response

    def validate_model(self, model: PredictiveModel, dataset: IndustrialDataset) -> ModelMetrics:
        """Validate model accuracy"""
        # Cross-validation, prediction error metrics
```

#### 4.2.2 MPC Controller
```python
class HybridMPCController:
    """Hybrid Model Predictive Controller"""

    def __init__(self, model: PredictiveModel):
        self.model = model
        self.prediction_horizon = 20
        self.control_horizon = 5

    def compute_control_action(self,
                              current_state: ProcessState,
                              setpoints: List[float],
                              constraints: ConstraintSet) -> List[float]:
        """Compute optimal control moves"""
        # Solve optimization problem
        # minimize: sum of squared errors + control effort
        # subject to: constraints on CVs, PVs, and rate of change
```

## 5. OPC-UA Integration

### 5.1 Real-Time Interface
```python
class OPCUAControlInterface:
    """High-performance OPC-UA client for PLC communication"""

    async def connect(self, server_url: str, credentials: Credentials):
        """Establish secure connection to OPC-UA server"""

    async def read_process_data(self) -> Dict[str, Any]:
        """High-speed buffered read of all process variables"""

    async def write_control_signals(self, control_actions: Dict[str, float]):
        """Write control signals with safety checks"""

    async def switch_control_mode(self, mode: ControlMode):
        """Handle manual/auto/cascade mode transitions"""
```

### 5.2 Safety & Reliability
```python
class SafetySystem:
    """Production safety and reliability features"""

    def validate_control_action(self, action: float, limits: ControlLimits) -> float:
        """Ensure control action is within safe limits"""

    def detect_abnormal_conditions(self, process_data: Dict) -> List[Alarm]:
        """Detect and alert on abnormal conditions"""

    def fallback_to_pid(self, reason: str):
        """Graceful degradation to PID control"""
```

## 6. Implementation Requirements

### 6.1 Technology Stack
- **Python 3.11+** with type hints
- **NumPy/Pandas** for data processing
- **scikit-learn/PyTorch** for ML models
- **asyncio** for real-time operations
- **python-opcua** for OPC-UA communication
- **FastAPI** for REST API
- **PostgreSQL/TimescaleDB** for time-series storage
- **Redis** for real-time caching
- **Docker** for containerization

### 6.2 Performance Requirements
- Data ingestion: >10,000 tags/second
- Control loop execution: <100ms latency
- Model training: <1 hour for typical dataset
- OPC-UA communication: <50ms round trip

### 6.3 Security Requirements
- Encrypted OPC-UA communication
- Role-based access control
- Audit trail for all control actions
- Fail-safe mechanisms
- Data validation and sanitization

## 7. Development Phases

### Phase 1: Core Infrastructure (Weeks 1-4)
- Dataset ingestion framework
- Variable type system
- Basic data validation

### Phase 2: Feature Engineering (Weeks 5-8)
- Time series feature extraction
- Cross-correlation analysis
- Data augmentation pipeline

### Phase 3: PID Optimization (Weeks 9-12)
- Classical tuning methods
- ML model development
- Performance metrics

### Phase 4: MPC Development (Weeks 13-16)
- Model identification
- Constraint handling
- Optimization solver

### Phase 5: OPC-UA Integration (Weeks 17-20)
- Real-time communication
- Safety systems
- Mode management

### Phase 6: Testing & Deployment (Weeks 21-24)
- Integration testing
- Performance optimization
- Production deployment

## 8. Example Usage

```python
# Initialize system
curator = DatasetCurator()
ai_supervisor = AISupervisor()
opc_interface = OPCUAInterface()

# Ingest historical data
dataset = curator.ingest_excel("data_beerfeed_03_02-05_09-2025.xls")

# Classify variables
dataset = curator.classify_variables(dataset)

# Train AI models
pid_optimizer = ai_supervisor.train_pid_optimizer(dataset)
mpc_model = ai_supervisor.train_mpc_model(dataset)

# Connect to PLC
await opc_interface.connect("opc.tcp://plc.local:4840")

# Real-time optimization loop
async def control_loop():
    while True:
        # Read current process state
        process_data = await opc_interface.read_process_data()

        # Compute optimal control
        if control_mode == "PID":
            control_action = pid_optimizer.compute(process_data)
        else:  # MPC
            control_action = mpc_model.compute(process_data)

        # Write to PLC
        await opc_interface.write_control_signals(control_action)

        await asyncio.sleep(0.1)  # 100ms control interval
```

## 9. Success Metrics

- **Control Performance**: 25% reduction in process variability
- **Optimization Speed**: <5 minutes to retune a control loop
- **Model Accuracy**: >95% prediction accuracy
- **System Reliability**: >99.9% uptime
- **User Adoption**: >80% of control loops using AI optimization

## 10. References

1. Basic Loop Tuning Methods (docs/basic_loop_tuning_methods.txt)
2. Model Based Tuning: IMC and Lambda Methods (docs/Model Based Tuning.txt)
3. Industrial dataset format (docs/data_beerfeed_03_02-05_09-2025.xls)
4. Ignition SCADA documentation
5. OPC-UA specification
6. ISA-95 standard for enterprise-control integration
