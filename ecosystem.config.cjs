module.exports = {
  apps: [
    {
      name: 'meeting-coach-fastapi',
      script: '/home/ubuntu/meeting-coach-fastapi/venv/bin/uvicorn',
      args: 'main:app --host 0.0.0.0 --port 4000',
      cwd: '/home/ubuntu/meeting-coach-fastapi',
      interpreter: '/bin/bash',
      env: {
        PYTHONPATH:
          '/home/ubuntu/meeting-coach-fastapi/venv/lib/python3.10/site-packages',
      },
    },
  ],
};
