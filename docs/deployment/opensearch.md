# OpenSearch Setup Guide

This comprehensive guide covers OpenSearch installation, configuration, optimization, and maintenance for the Multi-Modal Academic Research System.

## Table of Contents

1. [Overview](#overview)
2. [Installation Methods](#installation-methods)
3. [Configuration](#configuration)
4. [Index Management](#index-management)
5. [Security Configuration](#security-configuration)
6. [Performance Optimization](#performance-optimization)
7. [Cluster Setup](#cluster-setup)
8. [Backup and Restore](#backup-and-restore)
9. [Monitoring and Maintenance](#monitoring-and-maintenance)
10. [Troubleshooting](#troubleshooting)

## Overview

### What is OpenSearch?

OpenSearch is an open-source search and analytics engine derived from Elasticsearch. It provides:

- **Full-text search** with BM25 ranking
- **Vector search** with k-NN capabilities
- **Hybrid search** combining keyword and semantic search
- **Real-time indexing** and querying
- **Scalability** from single node to large clusters

### System Requirements

**Minimum (Development):**
- CPU: 2 cores
- RAM: 2GB
- Disk: 10GB

**Recommended (Production):**
- CPU: 4+ cores
- RAM: 8GB+ (16GB optimal)
- Disk: 50GB+ SSD
- Java: OpenJDK 11 or 17

## Installation Methods

### Method 1: Docker (Recommended for Development)

**Single Node Setup:**

```bash
# Pull latest OpenSearch image
docker pull opensearchproject/opensearch:latest

# Run single node with security disabled (development)
docker run -d \
  --name opensearch-dev \
  -p 9200:9200 \
  -p 9600:9600 \
  -e "discovery.type=single-node" \
  -e "OPENSEARCH_INITIAL_ADMIN_PASSWORD=MyStrongPassword123!" \
  -e "plugins.security.disabled=true" \
  -e "OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m" \
  opensearchproject/opensearch:latest

# Verify installation
curl http://localhost:9200

# Expected response:
{
  "name" : "opensearch-dev",
  "cluster_name" : "docker-cluster",
  "cluster_uuid" : "...",
  "version" : {
    "number" : "2.11.0",
    ...
  }
}
```

**With Persistence:**

```bash
# Create volume for data persistence
docker volume create opensearch-data

# Run with persistent storage
docker run -d \
  --name opensearch-dev \
  -p 9200:9200 \
  -p 9600:9600 \
  -e "discovery.type=single-node" \
  -e "OPENSEARCH_INITIAL_ADMIN_PASSWORD=MyStrongPassword123!" \
  -e "OPENSEARCH_JAVA_OPTS=-Xms1g -Xmx1g" \
  -v opensearch-data:/usr/share/opensearch/data \
  opensearchproject/opensearch:latest
```

### Method 2: Docker Compose

Create `opensearch-docker-compose.yml`:

```yaml
version: '3.8'

services:
  opensearch-node1:
    image: opensearchproject/opensearch:2.11.0
    container_name: opensearch-node1
    environment:
      - cluster.name=opensearch-cluster
      - node.name=opensearch-node1
      - discovery.type=single-node
      - bootstrap.memory_lock=true
      - "OPENSEARCH_JAVA_OPTS=-Xms1g -Xmx1g"
      - OPENSEARCH_INITIAL_ADMIN_PASSWORD=MyStrongPassword123!
    ulimits:
      memlock:
        soft: -1
        hard: -1
      nofile:
        soft: 65536
        hard: 65536
    volumes:
      - opensearch-data1:/usr/share/opensearch/data
    ports:
      - 9200:9200
      - 9600:9600
    networks:
      - opensearch-net

  opensearch-dashboards:
    image: opensearchproject/opensearch-dashboards:2.11.0
    container_name: opensearch-dashboards
    ports:
      - 5601:5601
    expose:
      - "5601"
    environment:
      OPENSEARCH_HOSTS: '["http://opensearch-node1:9200"]'
    networks:
      - opensearch-net
    depends_on:
      - opensearch-node1

volumes:
  opensearch-data1:

networks:
  opensearch-net:
```

Start services:

```bash
docker-compose -f opensearch-docker-compose.yml up -d

# Access OpenSearch: http://localhost:9200
# Access Dashboards: http://localhost:5601
```

### Method 3: Native Installation (Linux)

**Ubuntu/Debian:**

```bash
# Import OpenSearch GPG key
wget -qO - https://artifacts.opensearch.org/publickeys/opensearch.pgp | sudo gpg --dearmor -o /usr/share/keyrings/opensearch-keyring.gpg

# Add repository
echo "deb [signed-by=/usr/share/keyrings/opensearch-keyring.gpg] https://artifacts.opensearch.org/releases/bundle/opensearch/2.x/apt stable main" | sudo tee /etc/apt/sources.list.d/opensearch-2.x.list

# Update and install
sudo apt-get update
sudo apt-get install opensearch

# Configure
sudo nano /etc/opensearch/opensearch.yml

# Start service
sudo systemctl start opensearch
sudo systemctl enable opensearch

# Verify
curl http://localhost:9200
```

**CentOS/RHEL:**

```bash
# Create repo file
sudo tee /etc/yum.repos.d/opensearch-2.x.repo <<EOF
[opensearch-2.x]
name=OpenSearch 2.x
baseurl=https://artifacts.opensearch.org/releases/bundle/opensearch/2.x/yum
enabled=1
gpgcheck=1
gpgkey=https://artifacts.opensearch.org/publickeys/opensearch.pgp
EOF

# Install
sudo yum install opensearch

# Configure and start
sudo systemctl start opensearch
sudo systemctl enable opensearch
```

### Method 4: macOS (Homebrew)

```bash
# Tap OpenSearch
brew tap opensearch-project/opensearch

# Install OpenSearch
brew install opensearch

# Start service
brew services start opensearch

# Or start manually
opensearch
```

## Configuration

### Basic Configuration (opensearch.yml)

**Development Configuration:**

```yaml
# /etc/opensearch/opensearch.yml or config/opensearch.yml

# ======================== Cluster ========================
cluster.name: research-cluster
node.name: node-1

# ======================== Network ========================
network.host: 0.0.0.0
http.port: 9200

# ======================== Discovery ========================
discovery.type: single-node

# ======================== Memory ========================
bootstrap.memory_lock: true

# ======================== Paths ========================
path.data: /var/lib/opensearch
path.logs: /var/log/opensearch

# ======================== Security ========================
# Disable security for development
plugins.security.disabled: true

# ======================== Performance ========================
# Thread pools
thread_pool.search.size: 4
thread_pool.search.queue_size: 1000
thread_pool.write.size: 4
thread_pool.write.queue_size: 500
```

**Production Configuration:**

```yaml
# ======================== Cluster ========================
cluster.name: research-production-cluster
node.name: node-1
node.roles: [ master, data, ingest ]

# ======================== Network ========================
network.host: _site_
http.port: 9200
transport.port: 9300

# ======================== Discovery ========================
discovery.seed_hosts: ["node-1.example.com:9300", "node-2.example.com:9300"]
cluster.initial_master_nodes: ["node-1", "node-2", "node-3"]

# ======================== Memory ========================
bootstrap.memory_lock: true

# ======================== Security ========================
plugins.security.ssl.http.enabled: true
plugins.security.ssl.http.pemcert_filepath: certificates/node1.pem
plugins.security.ssl.http.pemkey_filepath: certificates/node1-key.pem
plugins.security.ssl.http.pemtrustedcas_filepath: certificates/root-ca.pem

# ======================== Performance ========================
indices.memory.index_buffer_size: 30%
indices.queries.cache.size: 10%
indices.fielddata.cache.size: 30%

# ======================== Circuit Breakers ========================
indices.breaker.total.limit: 70%
indices.breaker.request.limit: 40%
indices.breaker.fielddata.limit: 40%
```

### JVM Configuration (jvm.options)

```bash
# /etc/opensearch/jvm.options

# Heap size (set to 50% of available RAM, max 32GB)
-Xms4g
-Xmx4g

# GC configuration
-XX:+UseG1GC
-XX:G1ReservePercent=25
-XX:InitiatingHeapOccupancyPercent=30

# GC logging
-Xlog:gc*,gc+age=trace,safepoint:file=/var/log/opensearch/gc.log:utctime,pid,tags:filecount=32,filesize=64m

# Heap dumps on OOM
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/var/log/opensearch/

# Performance
-XX:+AlwaysPreTouch
-Djava.io.tmpdir=/tmp
```

### Environment Variables

```bash
# Set in .env or environment

# Connection
export OPENSEARCH_HOST=localhost
export OPENSEARCH_PORT=9200
export OPENSEARCH_USER=admin
export OPENSEARCH_PASSWORD=admin

# SSL/TLS
export OPENSEARCH_USE_SSL=false
export OPENSEARCH_VERIFY_CERTS=false

# Timeouts
export OPENSEARCH_TIMEOUT=30
export OPENSEARCH_RETRY_ON_TIMEOUT=true
export OPENSEARCH_MAX_RETRIES=3
```

## Index Management

### Create Research Index

**Python Code:**

```python
from opensearchpy import OpenSearch

# Connect to OpenSearch
client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    http_auth=('admin', 'admin'),
    use_ssl=False,
    verify_certs=False
)

# Define index mapping
index_mapping = {
    "settings": {
        "number_of_shards": 2,
        "number_of_replicas": 1,
        "refresh_interval": "1s",
        "index.knn": True,
        "index.knn.space_type": "cosinesimil",
        "analysis": {
            "analyzer": {
                "custom_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "stop", "snowball"]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "content_type": {
                "type": "keyword"
            },
            "title": {
                "type": "text",
                "analyzer": "custom_analyzer",
                "fields": {
                    "keyword": {"type": "keyword"}
                }
            },
            "abstract": {
                "type": "text",
                "analyzer": "custom_analyzer"
            },
            "content": {
                "type": "text",
                "analyzer": "custom_analyzer"
            },
            "authors": {
                "type": "keyword"
            },
            "publication_date": {
                "type": "date"
            },
            "embedding": {
                "type": "knn_vector",
                "dimension": 384,
                "method": {
                    "name": "hnsw",
                    "space_type": "cosinesimil",
                    "engine": "nmslib",
                    "parameters": {
                        "ef_construction": 128,
                        "m": 16
                    }
                }
            },
            "diagram_descriptions": {
                "type": "text"
            },
            "key_concepts": {
                "type": "keyword"
            },
            "citations": {
                "type": "nested",
                "properties": {
                    "text": {"type": "text"},
                    "source": {"type": "keyword"}
                }
            }
        }
    }
}

# Create index
client.indices.create(index='research_assistant', body=index_mapping)
print("Index created successfully!")
```

### Index Operations

```bash
# Using curl

# Create index
curl -X PUT "http://localhost:9200/research_assistant" -H 'Content-Type: application/json' -d @index_mapping.json

# Get index info
curl -X GET "http://localhost:9200/research_assistant"

# Get index settings
curl -X GET "http://localhost:9200/research_assistant/_settings"

# Get index mappings
curl -X GET "http://localhost:9200/research_assistant/_mapping"

# Update index settings (requires close/open)
curl -X POST "http://localhost:9200/research_assistant/_close"
curl -X PUT "http://localhost:9200/research_assistant/_settings" -H 'Content-Type: application/json' -d'
{
  "index": {
    "number_of_replicas": 2
  }
}'
curl -X POST "http://localhost:9200/research_assistant/_open"

# Delete index (WARNING: destroys data)
curl -X DELETE "http://localhost:9200/research_assistant"

# Reindex to new index
curl -X POST "http://localhost:9200/_reindex" -H 'Content-Type: application/json' -d'
{
  "source": {
    "index": "research_assistant"
  },
  "dest": {
    "index": "research_assistant_v2"
  }
}'
```

### Index Templates

Create templates for automatic index configuration:

```json
{
  "index_patterns": ["research_*"],
  "template": {
    "settings": {
      "number_of_shards": 2,
      "number_of_replicas": 1,
      "index.knn": true
    },
    "mappings": {
      "properties": {
        "timestamp": {
          "type": "date"
        },
        "embedding": {
          "type": "knn_vector",
          "dimension": 384
        }
      }
    }
  }
}
```

Apply template:

```bash
curl -X PUT "http://localhost:9200/_index_template/research_template" \
  -H 'Content-Type: application/json' \
  -d @template.json
```

## Security Configuration

### Enable Security Plugin

**1. Generate Certificates:**

```bash
# Create certificate directory
mkdir -p /etc/opensearch/certificates
cd /etc/opensearch/certificates

# Generate root CA
openssl genrsa -out root-ca-key.pem 2048
openssl req -new -x509 -sha256 -key root-ca-key.pem -out root-ca.pem -days 730 \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=root-ca"

# Generate node certificate
openssl genrsa -out node1-key.pem 2048
openssl req -new -key node1-key.pem -out node1.csr \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=node1.example.com"

# Sign node certificate
openssl x509 -req -in node1.csr -CA root-ca.pem -CAkey root-ca-key.pem \
  -CAcreateserial -sha256 -out node1.pem -days 365

# Set permissions
chmod 600 *-key.pem
chown opensearch:opensearch *
```

**2. Configure Security in opensearch.yml:**

```yaml
# Security
plugins.security.disabled: false

# SSL for HTTP
plugins.security.ssl.http.enabled: true
plugins.security.ssl.http.pemcert_filepath: certificates/node1.pem
plugins.security.ssl.http.pemkey_filepath: certificates/node1-key.pem
plugins.security.ssl.http.pemtrustedcas_filepath: certificates/root-ca.pem

# SSL for transport
plugins.security.ssl.transport.pemcert_filepath: certificates/node1.pem
plugins.security.ssl.transport.pemkey_filepath: certificates/node1-key.pem
plugins.security.ssl.transport.pemtrustedcas_filepath: certificates/root-ca.pem
plugins.security.ssl.transport.enforce_hostname_verification: false

# Authentication
plugins.security.authcz.admin_dn:
  - 'CN=admin,OU=SSL,O=Organization,L=City,ST=State,C=US'
```

**3. Configure Users:**

```bash
# Run security initialization
/usr/share/opensearch/plugins/opensearch-security/tools/securityadmin.sh \
  -cd /etc/opensearch/opensearch-security/ \
  -icl -nhnv \
  -cacert /etc/opensearch/certificates/root-ca.pem \
  -cert /etc/opensearch/certificates/admin.pem \
  -key /etc/opensearch/certificates/admin-key.pem
```

**4. Create Application User:**

```bash
# Create internal_users.yml
cat > /etc/opensearch/opensearch-security/internal_users.yml <<EOF
research_app_user:
  hash: "$2y$12$..."  # Generate with tools/hash.sh
  reserved: false
  backend_roles:
    - "research_app_role"
  description: "Research application user"
EOF

# Create roles_mapping.yml
cat > /etc/opensearch/opensearch-security/roles_mapping.yml <<EOF
research_app_role:
  reserved: false
  backend_roles:
    - "research_app_role"
  users:
    - "research_app_user"
EOF
```

### Authentication Methods

**1. Basic Authentication:**

```python
from opensearchpy import OpenSearch

client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    http_auth=('research_app_user', 'password'),
    use_ssl=True,
    verify_certs=True,
    ca_certs='/path/to/root-ca.pem'
)
```

**2. API Key Authentication:**

```bash
# Create API key
curl -X POST "https://localhost:9200/_plugins/_security/api/apikeys" \
  -u admin:admin \
  -H 'Content-Type: application/json' -d'
{
  "name": "research_app_key",
  "permissions": ["indices:data/read/*", "indices:data/write/*"]
}'

# Use in application
headers = {
    'Authorization': f'ApiKey {api_key_id}:{api_key}'
}
```

## Performance Optimization

### Index Optimization

**1. Shard Configuration:**

```python
# Optimal shard size: 10-50GB
# Formula: number_of_shards = total_data_size / 30GB

settings = {
    "number_of_shards": 2,  # For dataset < 60GB
    "number_of_replicas": 1,  # 1 replica for HA
    "refresh_interval": "30s",  # Reduce refresh frequency
    "translog.durability": "async",  # Better indexing performance
    "translog.sync_interval": "30s"
}
```

**2. Merge Policy:**

```json
{
  "settings": {
    "index.merge.policy.max_merged_segment": "5gb",
    "index.merge.policy.segments_per_tier": 10,
    "index.merge.scheduler.max_thread_count": 1
  }
}
```

**3. Codec Optimization:**

```json
{
  "settings": {
    "index.codec": "best_compression"
  }
}
```

### Query Optimization

**1. Use Filters Instead of Queries:**

```python
# Less optimal
query = {
    "query": {
        "bool": {
            "must": [
                {"match": {"content": "machine learning"}},
                {"match": {"content_type": "paper"}}
            ]
        }
    }
}

# Better - filter is cached
query = {
    "query": {
        "bool": {
            "must": [
                {"match": {"content": "machine learning"}}
            ],
            "filter": [
                {"term": {"content_type": "paper"}}
            ]
        }
    }
}
```

**2. Optimize Field Data:**

```json
{
  "mappings": {
    "properties": {
      "title": {
        "type": "text",
        "fields": {
          "keyword": {
            "type": "keyword"
          }
        }
      }
    }
  }
}
```

**3. Use Source Filtering:**

```python
# Only return necessary fields
search_body = {
    "_source": ["title", "abstract", "authors"],
    "query": {...}
}
```

### Hardware Optimization

**1. Disk:**
- Use SSD for best performance
- Separate OS, data, and log disks
- RAID 0 for data (if replicated)

**2. Memory:**
- Heap: 50% of RAM, max 32GB
- File system cache: remaining 50%

**3. CPU:**
- Modern CPU with good single-thread performance
- At least 4 cores

**4. Network:**
- 10Gb network for cluster communication
- Low latency between nodes

### Cache Configuration

```yaml
# opensearch.yml
indices.queries.cache.size: 10%
indices.fielddata.cache.size: 30%
indices.requests.cache.size: 2%
```

## Cluster Setup

### Single-Node Cluster (Development)

```yaml
cluster.name: dev-cluster
node.name: node-1
discovery.type: single-node
```

### Multi-Node Cluster (Production)

**Node 1 Configuration:**

```yaml
# opensearch.yml
cluster.name: production-cluster
node.name: node-1
node.roles: [ master, data, ingest ]

network.host: 192.168.1.10
http.port: 9200
transport.port: 9300

discovery.seed_hosts: ["192.168.1.10:9300", "192.168.1.11:9300", "192.168.1.12:9300"]
cluster.initial_master_nodes: ["node-1", "node-2", "node-3"]
```

**Node 2 Configuration:**

```yaml
cluster.name: production-cluster
node.name: node-2
node.roles: [ master, data, ingest ]

network.host: 192.168.1.11
http.port: 9200
transport.port: 9300

discovery.seed_hosts: ["192.168.1.10:9300", "192.168.1.11:9300", "192.168.1.12:9300"]
cluster.initial_master_nodes: ["node-1", "node-2", "node-3"]
```

**Node 3 Configuration:**

```yaml
cluster.name: production-cluster
node.name: node-3
node.roles: [ master, data, ingest ]

network.host: 192.168.1.12
http.port: 9200
transport.port: 9300

discovery.seed_hosts: ["192.168.1.10:9300", "192.168.1.11:9300", "192.168.1.12:9300"]
cluster.initial_master_nodes: ["node-1", "node-2", "node-3"]
```

### Dedicated Node Roles

**Master-eligible nodes:**

```yaml
node.roles: [ master ]
```

**Data nodes:**

```yaml
node.roles: [ data ]
```

**Coordinating nodes:**

```yaml
node.roles: []
```

### Cluster Health Monitoring

```bash
# Cluster health
curl http://localhost:9200/_cluster/health?pretty

# Node stats
curl http://localhost:9200/_nodes/stats?pretty

# Cluster stats
curl http://localhost:9200/_cluster/stats?pretty

# Pending tasks
curl http://localhost:9200/_cluster/pending_tasks?pretty
```

## Backup and Restore

### Snapshot Repository Setup

**1. Create Repository Directory:**

```bash
# Create backup directory
sudo mkdir -p /mnt/backups/opensearch
sudo chown opensearch:opensearch /mnt/backups/opensearch
```

**2. Configure Repository Path:**

```yaml
# opensearch.yml
path.repo: ["/mnt/backups/opensearch"]
```

**3. Register Repository:**

```bash
curl -X PUT "http://localhost:9200/_snapshot/backup_repo" -H 'Content-Type: application/json' -d'
{
  "type": "fs",
  "settings": {
    "location": "/mnt/backups/opensearch",
    "compress": true
  }
}'
```

### Create Snapshots

**Manual Snapshot:**

```bash
# Create snapshot
curl -X PUT "http://localhost:9200/_snapshot/backup_repo/snapshot_1?wait_for_completion=true" -H 'Content-Type: application/json' -d'
{
  "indices": "research_assistant",
  "ignore_unavailable": true,
  "include_global_state": false
}'

# List snapshots
curl -X GET "http://localhost:9200/_snapshot/backup_repo/_all?pretty"

# Get snapshot status
curl -X GET "http://localhost:9200/_snapshot/backup_repo/snapshot_1/_status?pretty"
```

**Automated Snapshots (Using Snapshot Management):**

```bash
# Create snapshot policy
curl -X PUT "http://localhost:9200/_plugins/_sm/policies/daily_snapshot" -H 'Content-Type: application/json' -d'
{
  "description": "Daily snapshot policy",
  "enabled": true,
  "snapshot_config": {
    "date_format": "yyyy-MM-dd-HH:mm",
    "timezone": "America/Los_Angeles",
    "indices": "*",
    "repository": "backup_repo",
    "ignore_unavailable": true,
    "include_global_state": false,
    "partial": false
  },
  "creation": {
    "schedule": {
      "cron": {
        "expression": "0 0 * * *",
        "timezone": "America/Los_Angeles"
      }
    }
  },
  "deletion": {
    "schedule": {
      "cron": {
        "expression": "0 1 * * *",
        "timezone": "America/Los_Angeles"
      }
    },
    "condition": {
      "max_age": "30d",
      "max_count": 30
    }
  }
}'
```

### Restore from Snapshot

```bash
# Close index before restore
curl -X POST "http://localhost:9200/research_assistant/_close"

# Restore snapshot
curl -X POST "http://localhost:9200/_snapshot/backup_repo/snapshot_1/_restore" -H 'Content-Type: application/json' -d'
{
  "indices": "research_assistant",
  "ignore_unavailable": true,
  "include_global_state": false,
  "rename_pattern": "(.+)",
  "rename_replacement": "restored_$1"
}'

# Monitor restore progress
curl -X GET "http://localhost:9200/_recovery?pretty"

# Open index after restore
curl -X POST "http://localhost:9200/research_assistant/_open"
```

### S3 Repository (Cloud Backup)

**1. Install S3 Plugin:**

```bash
/usr/share/opensearch/bin/opensearch-plugin install repository-s3
```

**2. Configure AWS Credentials:**

```bash
# Add credentials to keystore
/usr/share/opensearch/bin/opensearch-keystore add s3.client.default.access_key
/usr/share/opensearch/bin/opensearch-keystore add s3.client.default.secret_key
```

**3. Create S3 Repository:**

```bash
curl -X PUT "http://localhost:9200/_snapshot/s3_backup" -H 'Content-Type: application/json' -d'
{
  "type": "s3",
  "settings": {
    "bucket": "my-opensearch-backups",
    "region": "us-east-1",
    "base_path": "snapshots",
    "compress": true
  }
}'
```

## Monitoring and Maintenance

### Health Checks

```bash
# Cluster health
curl http://localhost:9200/_cluster/health?pretty

# Index health
curl http://localhost:9200/_cat/indices?v&health=yellow

# Shard allocation
curl http://localhost:9200/_cat/shards?v

# Node information
curl http://localhost:9200/_cat/nodes?v&h=name,node.role,heap.percent,ram.percent,cpu,load_1m,disk.used_percent
```

### Performance Metrics

```bash
# Index stats
curl http://localhost:9200/research_assistant/_stats?pretty

# Node stats
curl http://localhost:9200/_nodes/stats/indices,os,process,jvm,thread_pool?pretty

# Task management
curl http://localhost:9200/_tasks?detailed=true&actions=*search*&pretty

# Hot threads
curl http://localhost:9200/_nodes/hot_threads
```

### Monitoring Tools

**1. OpenSearch Dashboards:**

Access at http://localhost:5601

- Stack Management → Index Patterns
- Visualize → Create visualizations
- Dashboard → Monitor cluster

**2. Prometheus Exporter:**

```bash
# Install prometheus exporter
docker run -d \
  --name opensearch-exporter \
  -p 9114:9114 \
  -e OPENSEARCH_URI=http://opensearch:9200 \
  prometheuscommunity/opensearch-exporter:latest

# Scrape endpoint
curl http://localhost:9114/metrics
```

**3. Custom Monitoring Script:**

```python
import requests
from datetime import datetime

def monitor_cluster():
    base_url = "http://localhost:9200"

    # Cluster health
    health = requests.get(f"{base_url}/_cluster/health").json()
    print(f"Cluster Status: {health['status']}")
    print(f"Active Shards: {health['active_shards']}")

    # Index stats
    stats = requests.get(f"{base_url}/research_assistant/_stats").json()
    index_stats = stats['indices']['research_assistant']['total']
    print(f"Document Count: {index_stats['docs']['count']}")
    print(f"Store Size: {index_stats['store']['size_in_bytes'] / 1024 / 1024:.2f} MB")

    # Node stats
    nodes = requests.get(f"{base_url}/_nodes/stats").json()
    for node_id, node in nodes['nodes'].items():
        print(f"\nNode: {node['name']}")
        print(f"  Heap Used: {node['jvm']['mem']['heap_used_percent']}%")
        print(f"  CPU: {node['os']['cpu']['percent']}%")

if __name__ == "__main__":
    monitor_cluster()
```

### Maintenance Tasks

**1. Force Merge:**

```bash
# Force merge to reduce segments (run during low traffic)
curl -X POST "http://localhost:9200/research_assistant/_forcemerge?max_num_segments=1"
```

**2. Clear Cache:**

```bash
# Clear all caches
curl -X POST "http://localhost:9200/_cache/clear"

# Clear specific cache
curl -X POST "http://localhost:9200/research_assistant/_cache/clear?fielddata=true"
```

**3. Reindex:**

```bash
# Reindex for mapping changes
curl -X POST "http://localhost:9200/_reindex" -H 'Content-Type: application/json' -d'
{
  "source": {
    "index": "research_assistant"
  },
  "dest": {
    "index": "research_assistant_v2"
  }
}'
```

**4. Update Settings:**

```bash
# Update replica count
curl -X PUT "http://localhost:9200/research_assistant/_settings" -H 'Content-Type: application/json' -d'
{
  "index": {
    "number_of_replicas": 2
  }
}'
```

## Troubleshooting

### Common Issues

**1. Cluster Yellow/Red Status**

```bash
# Check shard allocation
curl http://localhost:9200/_cat/shards?v

# Explain unassigned shards
curl http://localhost:9200/_cluster/allocation/explain?pretty

# Force allocation
curl -X POST "http://localhost:9200/_cluster/reroute" -H 'Content-Type: application/json' -d'
{
  "commands": [
    {
      "allocate_replica": {
        "index": "research_assistant",
        "shard": 0,
        "node": "node-1"
      }
    }
  ]
}'
```

**2. Out of Memory Errors**

```bash
# Check heap usage
curl http://localhost:9200/_nodes/stats/jvm?pretty

# Increase heap size in jvm.options
-Xms4g
-Xmx4g

# Clear field data cache
curl -X POST "http://localhost:9200/_cache/clear?fielddata=true"
```

**3. Slow Queries**

```bash
# Enable slow log
curl -X PUT "http://localhost:9200/research_assistant/_settings" -H 'Content-Type: application/json' -d'
{
  "index.search.slowlog.threshold.query.warn": "10s",
  "index.search.slowlog.threshold.query.info": "5s",
  "index.search.slowlog.threshold.fetch.warn": "1s"
}'

# View slow log
tail -f /var/log/opensearch/research-cluster_index_search_slowlog.log
```

**4. Disk Space Issues**

```bash
# Check disk usage
curl http://localhost:9200/_cat/allocation?v

# Delete old indices
curl -X DELETE "http://localhost:9200/old_index"

# Set disk watermarks
curl -X PUT "http://localhost:9200/_cluster/settings" -H 'Content-Type: application/json' -d'
{
  "persistent": {
    "cluster.routing.allocation.disk.watermark.low": "85%",
    "cluster.routing.allocation.disk.watermark.high": "90%",
    "cluster.routing.allocation.disk.watermark.flood_stage": "95%"
  }
}'
```

### Debug Commands

```bash
# Detailed cluster state
curl http://localhost:9200/_cluster/state?pretty

# Thread pool stats
curl http://localhost:9200/_nodes/stats/thread_pool?pretty

# Circuit breaker stats
curl http://localhost:9200/_nodes/stats/breaker?pretty

# Segment stats
curl http://localhost:9200/_cat/segments/research_assistant?v

# Recovery status
curl http://localhost:9200/_cat/recovery?v&active_only=true
```

## Next Steps

- Review [Production Considerations](production.md) for deployment best practices
- See [Docker Deployment](docker.md) for containerized OpenSearch
- Check [Local Deployment](local.md) for development setup
