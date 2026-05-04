# executor.py

import asyncio

class Executor:

    async def run_agents(self, agents, transaction, registry):
        tasks = []

        for agent_name in agents:
            agent = registry.get(agent_name)
            tasks.append(agent.run(transaction))

        return await asyncio.gather(*tasks)