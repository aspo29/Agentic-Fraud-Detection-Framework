# for agent test in beginning
'''
from abc import ABC, abstractmethod

class BaseAgent(ABC):

    @abstractmethod
    def run(self, context):
        pass
        '''

#actual base agent code

from abc import ABC, abstractmethod
from core.agents.base.agent_result import AgentResult
from core.models.transaction_model import TransactionModel


class BaseAgent(ABC):

    @abstractmethod
    async def run(self, transaction: TransactionModel, context=None) -> AgentResult:
        """
        Every fraud agent MUST implement this.
        Must be async for orchestrator parallel execution.
        """
        pass