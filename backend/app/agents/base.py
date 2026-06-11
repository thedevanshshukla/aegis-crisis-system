from app.models import TaskState, AgentMessage

class BaseAgent:
    name: str = "BaseAgent"

    def run(self, state: TaskState) -> None:
        """Mutate state directly and log events using self.log()"""
        raise NotImplementedError("Each agent must implement the run method.")

    def log(self, state: TaskState, intent: str, action: str, reasoning: str, impact: str, data: dict = None):
        """Append a structured cognitive trace log to the task state logs."""
        from datetime import datetime
        timestamp_str = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        message = AgentMessage(
            agent=self.name,
            intent=intent,
            action=action,
            reasoning=reasoning,
            impact=impact,
            timestamp=timestamp_str,
            data=data or {}
        )
        state.logs.append(message)
