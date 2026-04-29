core/
│
├── orchestrator/
│   ├── orchestrator.py        # main entry: runs full fraud pipeline
│   ├── pipeline.py            # step execution logic (async workflow)
│   ├── context.py             # TransactionContext (shared object)
│   ├── router.py              # decides which agents to trigger
│   └── executor.py            # parallel execution (async / threading)
│
├── agents/
│   ├── base/
│   │   ├── base_agent.py      # abstract agent interface
│   │   └── agent_result.py    # standard output format (score, reason)
│   │
│   ├── velocity_agent/
│   │   ├── agent.py
│   │   ├── rules.py
│   │   ├── redis_store.py
│   │   └── lua_scripts/
│   │       └── velocity.lua
│   │
│   ├── geo_agent/
│   │   ├── agent.py
│   │   ├── distance_calc.py
│   │   ├── ip_lookup.py
│   │   └── rules.py
│   │
│   ├── behaviour_agent/
│   │   ├── agent.py
│   │   ├── profiler.py
│   │   ├── feature_extractor.py
│   │   └── baseline_model.py
│   │
│   └── synthesis_agent/
│       ├── agent.py
│       ├── weight_config.py
│       └── risk_fusion.py
│
├── decision_engine/
│   ├── scorer.py              # weighted scoring logic
│   ├── policy_engine.py       # business rules (ALLOW/BLOCK/REVIEW)
│   ├── thresholds.py
│   └── decision_model.py      # optional ML model
│
├── fraud_engine/
│   ├── rules_engine.py        # shared rule evaluation system
│   ├── risk_utils.py          # normalization, scaling
│   ├── anomaly_utils.py       # reusable anomaly detection helpers
│   ├── feature_store.py       # shared feature logic
│   └── constants.py
│
├── registry/
│   ├── agent_registry.py      # registers all agents dynamically
│   └── dependency_map.py      # defines agent dependencies/order
│
├── models/
│   ├── transaction_model.py   # internal transaction object
│   ├── risk_model.py          # risk score schema
│   └── agent_model.py         # agent input/output contracts
│
└── __init__.py


### Testing of the agents 

# manual testing 
PYTHONPATH=. python tests/test_velocity_agent.py OR create a env file 

# automated testing via pytest 

pip install pytest for testing 
PYTHONPATH=. pytest -v 
PYTHONPATH=. pytest -v -s  to have result with value 
PYTHONPATH=. pytest -v -s  test/test_velocity_performance.py

### Architecture of 
        Transaction
                ↓
        Orchestrator
                ↓
    Router → selects VelocityAgent
                ↓
    Executor (async parallel)
                 ↓
         VelocityAgent (Redis + Lua)
                ↓
        AgentResult(score + reason)
                ↓
        Synthesis Agent (future)
                ↓
    Decision Engine (BLOCK / REVIEW / ALLOW)


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
