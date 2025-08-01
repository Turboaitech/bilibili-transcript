import { Redis } from '@upstash/redis';

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL,
  token: process.env.UPSTASH_REDIS_REST_TOKEN,
});

export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method === 'GET') {
    // Get a pending task
    try {
      const taskId = await redis.rpop('pending_tasks');
      
      if (!taskId) {
        return res.status(200).json({ task: null });
      }

      const task = await redis.hgetall(taskId);
      
      if (!task || Object.keys(task).length === 0) {
        return res.status(200).json({ task: null });
      }

      // Update task status to processing
      await redis.hset(taskId, {
        ...task,
        status: 'processing',
        processingStartedAt: new Date().toISOString(),
      });

      res.status(200).json({
        task: {
          taskId,
          ...task,
        },
      });
    } catch (error) {
      console.error('Error getting pending task:', error);
      res.status(500).json({ error: 'Failed to get pending task' });
    }
  } else if (req.method === 'POST') {
    // Update task result
    const { taskId, result, error } = req.body;

    if (!taskId) {
      return res.status(400).json({ error: 'Task ID is required' });
    }

    try {
      const task = await redis.hgetall(taskId);
      
      if (!task || Object.keys(task).length === 0) {
        return res.status(404).json({ error: 'Task not found' });
      }

      // Update task with result
      await redis.hset(taskId, {
        ...task,
        status: error ? 'failed' : 'completed',
        result: result || null,
        error: error || null,
        completedAt: new Date().toISOString(),
      });

      res.status(200).json({
        success: true,
        message: 'Task updated successfully',
      });
    } catch (err) {
      console.error('Error updating task:', err);
      res.status(500).json({ error: 'Failed to update task' });
    }
  } else {
    res.status(405).json({ error: 'Method not allowed' });
  }
}