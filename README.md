# Checklist App

Simple Flask app to add, remove, and list checklists. Persists to Amazon ElastiCache for Redis using IAM authentication.

## Prerequisites

- Python 3.10+
- An ElastiCache for Redis cluster with **IAM authentication enabled** (Redis 7+, encryption in transit required)
- An IAM role (EC2 instance profile, ECS task role, EKS pod role, or Lambda role) with `elasticache:Connect` permission on the cluster + user
- A Redis user with `authentication-mode { Type = iam }` whose name matches the IAM identity

## IAM policy example

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "elasticache:Connect",
    "Resource": [
      "arn:aws:elasticache:<region>:<account>:replicationgroup:<cluster-name>",
      "arn:aws:elasticache:<region>:<account>:user:<redis-user>"
    ]
  }]
}
```

## Environment variables

| Var | Example |
| --- | --- |
| `AWS_REGION` | `us-east-1` |
| `ELASTICACHE_CLUSTER_NAME` | `my-checklist-cache` |
| `REDIS_HOST` | `my-checklist-cache.xxxx.ng.0001.use1.cache.amazonaws.com` |
| `REDIS_PORT` | `6379` |
| `REDIS_IAM_USER` | `checklist-app-user` |

AWS credentials come from the default boto3 provider chain — no static keys needed when running on EC2/ECS/EKS/Lambda with an attached role.

## Run

```bash
pip install -r requirements.txt
python app.py
```

Visit http://localhost:5000
