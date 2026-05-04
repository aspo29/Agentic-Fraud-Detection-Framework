# pipeline.py
'''
from core.registry.agent_registry import AgentRegistry

class Pipeline:
    def __init__(self):
        self.registry = AgentRegistry()

    def execute(self, context):
        agents = self.registry.get_active_agents(context)

        results = []

        for agent in agents:
            result = agent.run(context)
            results.append(result)
            context.add_result(result)

        return context.finalize()'''

class Pipeline:

    def __init__(self, router, executor, registry):
        self.router = router
        self.executor = executor
        self.registry = registry

    async def run(self, transaction):
        agents = self.router.route(transaction)

        results = await self.executor.run_agents(
            agents,
            transaction,
            self.registry
        )

        return results