import abc
import json
import asyncio
import os
from typing import Dict, Any, List, Tuple, Optional
from app.utils.logger import logger
from app.utils.config import settings

# Attempt to import redis for production environment
try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

class MessageBus(abc.ABC):
    """
    Abstract message bus interface for event-driven agent communication.
    """
    @abc.abstractmethod
    async def publish(self, stream: str, data: Dict[str, Any]) -> str:
        """
        Publishes a message (dict) to the specified stream.
        Returns the unique message ID.
        """
        pass

    @abc.abstractmethod
    async def read_stream(
        self, 
        stream: str, 
        group: str, 
        consumer: str, 
        count: int = 1, 
        block_ms: int = 2000
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Reads messages from a stream using a consumer group.
        Returns a list of tuples: (message_id, data_dict).
        """
        pass

    @abc.abstractmethod
    async def acknowledge(self, stream: str, group: str, message_id: str):
        """
        Acknowledges a message in the stream for the specified consumer group.
        """
        pass

    @abc.abstractmethod
    async def close(self):
        """
        Closes any active connections.
        """
        pass


class RedisMessageBus(MessageBus):
    """
    Production Redis Streams implementation of MessageBus.
    """
    def __init__(self, host: str = "redis", port: int = 6379, db: int = 0):
        if not REDIS_AVAILABLE:
            raise RuntimeError("redis package is not installed. Please install redis.")
        
        # Connect to Redis using connection pool
        redis_url = f"redis://{host}:{port}/{db}"
        self.pool = aioredis.ConnectionPool.from_url(redis_url, decode_responses=True)
        self.client = aioredis.Redis(connection_pool=self.pool)
        self._created_groups = set()
        logger.info(f"Connected to Redis message bus at {redis_url}")

    async def publish(self, stream: str, data: Dict[str, Any]) -> str:
        # Serialise fields to strings for Redis
        serialized_data = {}
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                serialized_data[k] = json.dumps(v)
            else:
                serialized_data[k] = str(v)
        
        msg_id = await self.client.xadd(stream, serialized_data)
        logger.debug(f"[Redis Message Bus] Published to stream '{stream}': {msg_id}")
        return msg_id

    async def _ensure_group(self, stream: str, group: str):
        group_key = f"{stream}:{group}"
        if group_key in self._created_groups:
            return

        try:
            # Create stream and consumer group starting at '$' (only new messages)
            # MKSTREAM will auto-create the stream if it doesn't exist
            await self.client.xgroup_create(stream, group, id="$", mkstream=True)
            logger.info(f"[Redis Message Bus] Created consumer group '{group}' on stream '{stream}'")
        except Exception as e:
            # Group already exists error is fine to ignore
            if "BUSYGROUP" in str(e):
                pass
            else:
                logger.error(f"[Redis Message Bus] Error creating group {group} on {stream}: {e}")
                raise
        
        self._created_groups.add(group_key)

    async def read_stream(
        self, 
        stream: str, 
        group: str, 
        consumer: str, 
        count: int = 1, 
        block_ms: int = 2000
    ) -> List[Tuple[str, Dict[str, Any]]]:
        await self._ensure_group(stream, group)
        
        try:
            # Read new messages (indicated by '>')
            results = await self.client.xreadgroup(
                groupname=group,
                consumername=consumer,
                streams={stream: ">"},
                count=count,
                block=block_ms
            )
            
            messages = []
            if results:
                for stream_name, msgs in results:
                    for msg_id, raw_data in msgs:
                        # Deserialize json objects if valid json
                        deserialized_data = {}
                        for k, v in raw_data.items():
                            try:
                                deserialized_data[k] = json.loads(v)
                            except (json.JSONDecodeError, TypeError):
                                deserialized_data[k] = v
                        messages.append((msg_id, deserialized_data))
            return messages
        except Exception as e:
            logger.error(f"[Redis Message Bus] Error reading stream {stream}: {e}")
            return []

    async def acknowledge(self, stream: str, group: str, message_id: str):
        try:
            await self.client.xack(stream, group, message_id)
            logger.debug(f"[Redis Message Bus] Acknowledged message {message_id} in {stream} for group {group}")
        except Exception as e:
            logger.error(f"[Redis Message Bus] Failed to acknowledge message {message_id} in {stream}: {e}")

    async def close(self):
        await self.client.aclose()
        await self.pool.disconnect()
        logger.info("Closed Redis connection pool.")


class InMemoryMessageBus(MessageBus):
    """
    In-memory mock MessageBus implementation for local/unit testing.
    Uses asyncio.Queue to route messages.
    """
    def __init__(self):
        self._queues: Dict[str, asyncio.Queue] = {}
        self._msg_counter = 0
        self._lock = asyncio.Lock()
        logger.info("Initialized In-Memory message bus.")

    def _get_queue(self, stream: str) -> asyncio.Queue:
        if stream not in self._queues:
            self._queues[stream] = asyncio.Queue()
        return self._queues[stream]

    async def publish(self, stream: str, data: Dict[str, Any]) -> str:
        async with self._lock:
            self._msg_counter += 1
            msg_id = f"inmem-{self._msg_counter}"
        
        queue = self._get_queue(stream)
        # Store copy of data to prevent in-place modifications between processes
        copied_data = json.loads(json.dumps(data))
        await queue.put((msg_id, copied_data))
        logger.debug(f"[InMemory Message Bus] Published to '{stream}': {msg_id}")
        return msg_id

    async def read_stream(
        self, 
        stream: str, 
        group: str, 
        consumer: str, 
        count: int = 1, 
        block_ms: int = 2000
    ) -> List[Tuple[str, Dict[str, Any]]]:
        queue = self._get_queue(stream)
        messages = []
        
        try:
            # If blocking read, wait for at least one message or timeout
            if block_ms > 0:
                try:
                    # Convert ms to seconds
                    timeout = block_ms / 1000.0
                    msg = await asyncio.wait_for(queue.get(), timeout=timeout)
                    messages.append(msg)
                except asyncio.TimeoutError:
                    pass
            
            # Consume any other pending messages immediately up to count
            while len(messages) < count and not queue.empty():
                msg = queue.get_nowait()
                messages.append(msg)
                
        except Exception as e:
            logger.error(f"[InMemory Message Bus] Read stream error: {e}")
            
        return messages

    async def acknowledge(self, stream: str, group: str, message_id: str):
        # Acknowledge is a no-op for mock queue
        pass

    async def close(self):
        pass


# Global function to retrieve the configured message bus
_global_bus = None

def get_message_bus() -> MessageBus:
    """
    Returns a singleton instance of the MessageBus, determined by environment.
    """
    global _global_bus
    if _global_bus is None:
        use_redis = os.environ.get("USE_REDIS", "false").lower() == "true"
        if use_redis:
            host = os.environ.get("REDIS_HOST", "redis")
            port = int(os.environ.get("REDIS_PORT", "6379"))
            _global_bus = RedisMessageBus(host=host, port=port)
        else:
            _global_bus = InMemoryMessageBus()
    return _global_bus
