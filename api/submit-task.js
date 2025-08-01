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

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { videoUrl } = req.body;

  if (!videoUrl) {
    return res.status(400).json({ error: 'Video URL is required' });
  }

  // Extract video ID from URL
  const videoIdMatch = videoUrl.match(/(?:BV[\w]+|av\d+)/i);
  if (!videoIdMatch) {
    return res.status(400).json({ error: 'Invalid Bilibili video URL' });
  }

  const videoId = videoIdMatch[0];
  const taskId = `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

  try {
    // Store task in Redis
    await redis.hset(taskId, {
      videoUrl,
      videoId,
      status: 'pending',
      createdAt: new Date().toISOString(),
      result: null,
    });

    // Add to pending queue
    await redis.lpush('pending_tasks', taskId);

    // Set expiration (24 hours)
    await redis.expire(taskId, 86400);

    res.status(200).json({
      success: true,
      taskId,
      message: 'Task submitted successfully',
    });
  } catch (error) {
    console.error('Error submitting task:', error);
    res.status(500).json({ error: 'Failed to submit task' });
  }
}