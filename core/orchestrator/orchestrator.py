# orchestrator.py

'''from core.orchestrator.context import TransactionContext
from core.orchestrator.pipeline import Pipeline

class Orchestrator:
    def __init__(self):
        self.pipeline = Pipeline()

    def run(self, transaction: dict):
        context = TransactionContext(transaction)

        result = self.pipeline.execute(context)

        return result'''
    

class Orchestrator:

    def __init__(self, pipeline):
        self.pipeline = pipeline

    async def process(self, transaction):
        return await self.pipeline.run(transaction)