### Testing of the agents 

# manual testing 
PYTHONPATH=. python tests/test_velocity_agent.py OR create a env file 

# automated testing via pytest 

pip install pytest for testing 
PYTHONPATH=. pytest -v 
PYTHONPATH=. pytest -v -s  to have result with value 
PYTHONPATH=. pytest -v -s  test/test_velocity_performance.py

### dataflow pipeline diagram 
                        transactions.raw (Kafka)
                                  ↓
                        Orchestrator Consumer
                                  ↓
                        Router Service
                                 ↓
                        Executor Pool (async workers)
                                 ↓
                        VelocityAgent  ↔ Redis (sliding window)
                                 ↓
                        GeoAgent
                                ↓
                        BehavioralAgent
                                ↓
                        SyntheticAgent (fusion of all agent scores)
                                ↓
                        Synthesis / Aggregation Layer
                                ↓
                        Decision Engine
                                 ↓
                        fraud.decision (Kafka)
                               ↓
                        BLOCK / REVIEW / ALLOW

##file structure 
core/
│
├── orchestrator/
│   ├── orchestrator.py        # entry point (runs pipeline)
│   ├── pipeline.py            # async workflow execution
│   ├── router.py              # routes transaction → agents
│   ├── executor.py            # parallel execution engine (future scaling)
│   └── context.py             # shared TransactionContext
│
│
├── infrastructure/
│   │
│   ├── kafka/
│   │   ├── consumer.py        # Kafka ingestion (transactions.raw)
│   │   ├── producer.py        # Kafka output publisher
│   │   └── topics.py          # topic constants
│   │
│   ├── redis/
│   │   ├── redis_client.py    # Redis connection manager
│   │   └── base_store.py      # shared Redis utilities
│   │
│   └── logging/
│       └── logger.py          # structured logging config
│
│
├── agents/
│   │
│   ├── base/
│   │   ├── base_agent.py      # abstract agent interface
│   │   └── agent_result.py    # standard output contract
│   │
│   ├── schemas.py             # Pydantic models (ALL agent outputs)
│   │
│   ├── velocity_agent/
│   │   ├── agent.py           # orchestration logic
│   │   ├── rules.py           # fraud scoring rules (pure logic)
│   │   ├── redis_store.py     # ZSET + Lua interaction
│   │   └── lua_scripts/
│   │       └── velocity.lua   # atomic sliding window logic
│   │
│   ├── geo_agent/
│   │   ├── agent.py
│   │   ├── rules.py
│   │   └── geo_store.py
│   │
│   ├── behaviour_agent/
│   │   ├── agent.py
│   │   ├── sequence_model.py
│   │   └── feature_builder.py
│   │
│   └── synthesis_agent/
│       ├── agent.py
│       ├── scorer.py
│       └── risk_aggregator.py
│
│
├── decision_engine/
│   ├── scorer.py              # combines agent outputs
│   ├── policy_engine.py       # ALLOW / BLOCK / REVIEW rules
│   ├── thresholds.py          # risk thresholds config
│   └── decision_model.py      # optional ML layer
│
│
├── fraud_engine/
│   ├── rules_engine.py        # shared rule evaluation framework
│   ├── risk_utils.py          # normalization functions
│   ├── anomaly_utils.py       # anomaly detection helpers
│   ├── feature_store.py       # shared feature computation
│   └── constants.py
│
│
├── registry/
│   ├── agent_registry.py      # dynamic agent registration
│   └── dependency_map.py      # execution order / DAG config
│
│
├── models/
│   ├── transaction_model.py   # core transaction schema
│   ├── risk_model.py          # final risk output schema
│   └── agent_model.py         # agent I/O contracts
│
│
├── tests/
│   ├── test_velocity_agent.py
│   ├── test_geo_agent.py
│   ├── test_pipeline.py
│   └── test_decision_engine.py
│
│
└── __init__.py

##need to work on the following things after building other agents (velocity)
fallback in process()
real Redis wiring
final tests
metrics/logging
