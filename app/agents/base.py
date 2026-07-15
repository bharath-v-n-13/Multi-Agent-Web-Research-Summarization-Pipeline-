import abc
import asyncio
import traceback
from typing import Dict, Any, Optional
from app.utils.message_bus import MessageBus, get_message_bus
from app.utils.logger import logger

class AbstractAgent(abc.ABC):
    """
    Abstract base class defining the standard agent contract.
    """
    @abc.abstractmethod
    async def process_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the agent's core reasoning or action.
        Receives request parameters / current state, returns updated state slice.
        """
        pass


class BaseWorkerAgent(AbstractAgent, abc.ABC):
    """
    Standard daemon worker agent class that consumes from a Message Bus stream,
    processes messages, and publishes results back.
    """
    def __init__(
        self,
        agent_name: str,
        input_stream: str,
        output_stream: str,
        concurrency_limit: int = 10,
        bus: Optional[MessageBus] = None
    ):
        self.agent_name = agent_name
        self.input_stream = input_stream
        self.output_stream = output_stream
        self.concurrency_limit = concurrency_limit
        self.bus = bus or get_message_bus()
        self.semaphore = asyncio.Semaphore(concurrency_limit)
        self.running = False
        self.active_tasks = set()

    async def run_forever(self):
        """
        Runs the main message consumption loop until stopped.
        """
        self.running = True
        logger.info(f"[{self.agent_name}] Agent worker started. Input: '{self.input_stream}' | Concurrency: {self.concurrency_limit}")
        
        consumer_name = f"consumer-{self.agent_name}"
        group_name = f"group-{self.agent_name}"
        
        while self.running:
            try:
                # Wait for slot in concurrency limits before reading
                await self.semaphore.acquire()
                
                # Fetch a message. Blocking read (up to 2 seconds)
                messages = await self.bus.read_stream(
                    stream=self.input_stream,
                    group=group_name,
                    consumer=consumer_name,
                    count=1,
                    block_ms=2000
                )
                
                if not messages:
                    # No message, release semaphore slot and loop
                    self.semaphore.release()
                    await asyncio.sleep(0.1)
                    continue
                
                msg_id, message_data = messages[0]
                logger.debug(f"[{self.agent_name}] Received task message {msg_id}")
                
                # Spawn task to process the message asynchronously
                task = asyncio.create_task(
                    self._safe_process_message(msg_id, message_data, group_name)
                )
                self.active_tasks.add(task)
                # Remove from tracking set on completion
                task.add_done_callback(self.active_tasks.discard)
                
            except asyncio.CancelledError:
                self.running = False
                break
            except Exception as e:
                logger.error(f"[{self.agent_name}] Error in run loop: {e}")
                # Ensure we release the semaphore slot on error
                self.semaphore.release()
                await asyncio.sleep(1.0)
                
        # Wait for all active tasks to complete on shutdown
        if self.active_tasks:
            logger.info(f"[{self.agent_name}] Shutting down, waiting for {len(self.active_tasks)} active tasks...")
            await asyncio.gather(*self.active_tasks, return_exceptions=True)
            
        logger.info(f"[{self.agent_name}] Agent worker stopped.")

    async def _safe_process_message(self, msg_id: str, message_data: Dict[str, Any], group_name: str):
        try:
            # Process the actual message logic
            result = await self.process_message(message_data)
            
            # Send result to output stream
            if result is not None and self.output_stream:
                # Ensure the request correlation info (e.g., report_id, topic) is maintained
                correlation_keys = ["report_id", "topic", "iteration", "meta"]
                for key in correlation_keys:
                    if key in message_data and key not in result:
                        result[key] = message_data[key]
                
                await self.bus.publish(self.output_stream, result)
                
            # Acknowledge the message
            await self.bus.acknowledge(self.input_stream, group_name, msg_id)
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] Failed to process message {msg_id}: {e}\n{traceback.format_exc()}")
            
            # Publish failure message to supervisor or output stream so the system doesn't hang
            fail_payload = {
                "report_id": message_data.get("report_id"),
                "topic": message_data.get("topic"),
                "error": str(e),
                "agent": self.agent_name,
                "status": "failed"
            }
            try:
                # Direct to supervisor
                await self.bus.publish("stream:supervisor:errors", fail_payload)
            except Exception as publish_error:
                logger.error(f"[{self.agent_name}] Failed to publish error payload: {publish_error}")
                
            # Acknowledge the original failed message to avoid stuck messages (retries managed by Supervisor)
            await self.bus.acknowledge(self.input_stream, group_name, msg_id)
            
        finally:
            # Release slot
            self.semaphore.release()

    def stop(self):
        self.running = False
