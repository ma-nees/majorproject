# Fraud Detection Platform Architecture

The system is composed of several independent services that work together to detect fraudulent activities in real-time.

```mermaid
graph TD
    %% Define Styles
    classDef external fill:#f9f,stroke:#333,stroke-width:2px;
    classDef streaming fill:#ffa,stroke:#333,stroke-width:2px;
    classDef processing fill:#bbf,stroke:#333,stroke-width:2px;
    classDef ml fill:#bfb,stroke:#333,stroke-width:2px;
    classDef data fill:#fbb,stroke:#333,stroke-width:2px;
    classDef frontend fill:#dff,stroke:#333,stroke-width:2px;

    %% External Sources
    ClientApp[Client Application]:::external
    WebPortal[Web Portal]:::external

    %% Ingestion Layer
    API[API Gateway\nFastAPI]:::processing
    Auth[Authentication]:::processing
    
    %% Streaming Engine
    Kafka[Kafka Event Bus]:::streaming
    
    %% Data Processing
    FeatureExtractor[Feature Extraction Service]:::processing
    BehavBio[Behavioral Biometrics Analysis]:::processing
    
    %% ML & Risk Engine
    Anomaly[Anomaly Detection]:::ml
    RiskCalc[Risk Engine Calculator]:::ml
    MLPipeline[Machine Learning Pipeline]:::ml
    
    %% Storage
    DB[(Operational Database\nPostgreSQL)]:::data
    Lake[(Data Lake\nDelta Lake/S3)]:::data
    Cache[(Feature Cache\nRedis)]:::data
    
    %% Frontend and Action
    Dashboard[Frontend Dashboard\nReact.js]:::frontend
    Alerts[Alert Notification Service]:::processing

    %% Connections
    ClientApp -->|HTTP/REST| API
    WebPortal -->|HTTP/REST| API
    
    API --> Auth
    API -->|Raw Events| Kafka
    
    Kafka --> FeatureExtractor
    Kafka --> BehavBio
    Kafka --> Lake
    
    FeatureExtractor --> Cache
    BehavBio --> Cache
    
    Cache --> RiskCalc
    Cache --> Anomaly
    
    Anomaly --> RiskCalc
    MLPipeline -.->|Updates Models| Anomaly
    MLPipeline -.->|Updates Models| RiskCalc
    
    Lake -.->|Training Data| MLPipeline
    
    RiskCalc -->|Fraud Predictions| Kafka
    RiskCalc --> DB
    
    Kafka --> Alerts
    
    Dashboard -->|Reads State| API
    DB --> Dashboard
    Alerts --> Dashboard
```

## Description of Components

1. **Ingestion Layer:** The `API Gateway` acts as the single entry point for all transaction and behavior logs, performing basic authentication before forwarding logs as events.
2. **Streaming Engine:** `Kafka Event Bus` allows multiple asynchronous services to subscribe to raw transaction events (for processing, logging, scaling, etc.) without blocking the main API response path.
3. **Data Processing:** Specialized workers such as the `Feature Extraction Service` and `Behavioral Biometrics Analysis` enrich the transactions with historical aggregated features derived from real-time streams and fetched from a quick `Feature Cache`.
4. **Machine Learning & Risk Engine:** Using loaded models, incoming events are evaluated by `Anomaly Detection` models (like Isolation Forests) and rule-based or supervised models within the `Risk Engine Calculator` to assign a definitive risk score.
5. **Storage:** Relational `Operational Database` holds finalized transaction states, user data, and risk decisions. The `Data Lake` stores all historical raw events for offline `Machine Learning Pipeline` training. 
6. **Actions & Dashboard:** The `Alert Notification Service` triggers if thresholds are crossed, sending out emails/SMS mapping to High-Risk actions. A `Frontend Dashboard` offers security teams interactive insights and reports.
