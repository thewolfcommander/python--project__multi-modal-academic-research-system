# OpenSearch Troubleshooting Guide

Comprehensive troubleshooting guide for OpenSearch-related issues in the Multi-Modal Academic Research System.

## Table of Contents

- [Connection Issues](#connection-issues)
- [Indexing Failures](#indexing-failures)
- [Search Performance Problems](#search-performance-problems)
- [Memory Issues](#memory-issues)
- [Cluster Health](#cluster-health)
- [Index Corruption](#index-corruption)
- [Mapping Conflicts](#mapping-conflicts)
- [Diagnostic Commands](#diagnostic-commands)

---

## Connection Issues

### Cannot connect to OpenSearch

**Symptoms**:
- `ConnectionError: Connection refused`
- `ConnectionTimeout`
- `TransportError(N/A, 'Unable to connect')`

**Diagnosis**:
```bash
# Check if OpenSearch is running
curl http://localhost:9200

# Check Docker containers
docker ps | grep opensearch

# Check port availability
lsof -i :9200
netstat -an | grep 9200
```

**Solutions**:

1. **Start OpenSearch if not running**:
```bash
docker run -d \
  --name opensearch-node \
  -p 9200:9200 -p 9600:9600 \
  -e "discovery.type=single-node" \
  -e "DISABLE_SECURITY_PLUGIN=true" \
  opensearchproject/opensearch:latest
```

2. **Check Docker daemon**:
```bash
# Ensure Docker is running
docker info

# Restart Docker if needed
# Mac: Restart Docker Desktop
# Linux: sudo systemctl restart docker
```

3. **Verify network configuration**:
```bash
# Test connectivity
telnet localhost 9200

# Check firewall rules
sudo iptables -L | grep 9200  # Linux
# or
sudo pfctl -s rules | grep 9200  # Mac
```

4. **Fix host/port mismatch**:
```python
# In opensearch_manager.py
client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    http_compress=True,
    use_ssl=False,
    verify_certs=False,
    timeout=30
)
```

---

### SSL/TLS Connection Errors

**Symptoms**:
- `SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]`
- `ConnectionError: Caused by SSLError`

**Solutions**:

1. **Disable SSL for local development**:
```bash
docker run -d \
  --name opensearch-node \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "DISABLE_SECURITY_PLUGIN=true" \
  -e "plugins.security.ssl.http.enabled=false" \
  opensearchproject/opensearch:latest
```

2. **Update client configuration**:
```python
from opensearchpy import OpenSearch

client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    http_compress=True,
    use_ssl=False,
    verify_certs=False,
    ssl_show_warn=False
)
```

---

### Authentication Failures

**Symptoms**:
- `AuthenticationException`
- `403 Forbidden`
- `401 Unauthorized`

**Solutions**:

1. **Disable security for local development**:
```bash
docker run -d \
  --name opensearch-node \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "DISABLE_SECURITY_PLUGIN=true" \
  opensearchproject/opensearch:latest
```

2. **Use basic authentication** (if security enabled):
```python
client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    http_auth=('admin', 'admin'),  # Default credentials
    use_ssl=True,
    verify_certs=False
)
```

---

## Indexing Failures

### Index Creation Fails

**Symptoms**:
- `RequestError: resource_already_exists_exception`
- `TransportError(400, 'illegal_argument_exception')`

**Diagnosis**:
```bash
# Check if index exists
curl http://localhost:9200/_cat/indices?v

# Get index details
curl http://localhost:9200/research_assistant
```

**Solutions**:

1. **Delete existing index** (WARNING: loses data):
```bash
curl -X DELETE http://localhost:9200/research_assistant
```

2. **Handle in code**:
```python
from opensearchpy.exceptions import RequestError

try:
    client.indices.create(index='research_assistant', body=settings)
except RequestError as e:
    if e.error == 'resource_already_exists_exception':
        print(f"Index already exists")
    else:
        raise
```

3. **Use index templates for reusability**:
```python
index_template = {
    "index_patterns": ["research_*"],
    "template": {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "properties": {
                "embedding": {
                    "type": "knn_vector",
                    "dimension": 384
                }
            }
        }
    }
}

client.indices.put_index_template(
    name='research_template',
    body=index_template
)
```

---

### Bulk Indexing Errors

**Symptoms**:
- `BulkIndexError`
- Documents not appearing in index
- Partial indexing success

**Diagnosis**:
```python
# Check bulk response
response = client.bulk(body=bulk_data)

if response['errors']:
    for item in response['items']:
        if 'error' in item.get('index', {}):
            print(f"Error: {item['index']['error']}")
```

**Solutions**:

1. **Handle errors gracefully**:
```python
from opensearchpy import helpers

def index_documents(documents):
    actions = [
        {
            "_index": "research_assistant",
            "_id": doc['id'],
            "_source": doc
        }
        for doc in documents
    ]

    success, failed = helpers.bulk(
        client,
        actions,
        raise_on_error=False,
        raise_on_exception=False
    )

    print(f"Indexed: {success}, Failed: {len(failed)}")

    for item in failed:
        print(f"Failed document: {item}")
```

2. **Reduce batch size**:
```python
def index_in_batches(documents, batch_size=100):
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        helpers.bulk(client, prepare_actions(batch))
        time.sleep(1)  # Rate limiting
```

3. **Validate data before indexing**:
```python
def validate_document(doc):
    required_fields = ['id', 'title', 'content']
    for field in required_fields:
        if field not in doc:
            raise ValueError(f"Missing field: {field}")

    # Validate embedding dimension
    if 'embedding' in doc:
        if len(doc['embedding']) != 384:
            raise ValueError(f"Invalid embedding dimension")

    return True
```

---

### Mapping Conflicts

**Symptoms**:
- `mapper_parsing_exception`
- `illegal_argument_exception: mapper [field] cannot be changed`

**Diagnosis**:
```bash
# Get current mapping
curl http://localhost:9200/research_assistant/_mapping?pretty

# Check field types
curl http://localhost:9200/research_assistant/_mapping/field/embedding
```

**Solutions**:

1. **Reindex with correct mapping**:
```python
# Create new index with correct mapping
new_index_settings = {
    "mappings": {
        "properties": {
            "embedding": {
                "type": "knn_vector",
                "dimension": 384
            },
            "publication_date": {
                "type": "date",
                "format": "yyyy-MM-dd||epoch_millis"
            }
        }
    }
}

client.indices.create(index='research_assistant_v2', body=new_index_settings)

# Reindex data
client.reindex(
    body={
        "source": {"index": "research_assistant"},
        "dest": {"index": "research_assistant_v2"}
    }
)

# Switch alias
client.indices.delete_alias(index='research_assistant', name='research')
client.indices.put_alias(index='research_assistant_v2', name='research')
```

2. **Use dynamic mapping carefully**:
```python
index_settings = {
    "settings": {
        "index": {
            "mapping": {
                "ignore_malformed": True,  # Ignore badly formatted data
                "coerce": True  # Try to convert types
            }
        }
    }
}
```

---

## Search Performance Problems

### Slow Query Performance

**Symptoms**:
- Queries taking > 5 seconds
- Timeout errors
- High CPU usage

**Diagnosis**:
```bash
# Check query performance
curl -X GET "localhost:9200/research_assistant/_search?pretty" \
  -H 'Content-Type: application/json' \
  -d '{"profile": true, "query": {"match_all": {}}}'

# Check cluster stats
curl http://localhost:9200/_cluster/stats?pretty

# Monitor slow queries
curl http://localhost:9200/_nodes/stats/indices/search?pretty
```

**Solutions**:

1. **Optimize query structure**:
```python
# Use filters instead of queries when possible (cached)
query = {
    "query": {
        "bool": {
            "must": [
                {"match": {"content": query_text}}
            ],
            "filter": [  # Filters are faster and cached
                {"term": {"content_type": "paper"}},
                {"range": {"publication_date": {"gte": "2020-01-01"}}}
            ]
        }
    }
}
```

2. **Add result size limits**:
```python
results = client.search(
    index='research_assistant',
    body=query,
    size=10,  # Limit results
    request_timeout=30
)
```

3. **Use pagination for large result sets**:
```python
from opensearchpy import helpers

def search_with_pagination(query, page_size=100):
    results = helpers.scan(
        client,
        index='research_assistant',
        query=query,
        size=page_size,
        scroll='2m'
    )

    for hit in results:
        yield hit
```

4. **Optimize kNN search**:
```python
# Reduce candidates for kNN
knn_query = {
    "size": 10,
    "query": {
        "knn": {
            "embedding": {
                "vector": query_embedding,
                "k": 10,  # Number of nearest neighbors
                "method_parameters": {
                    "ef_search": 100  # Reduce for faster search
                }
            }
        }
    }
}
```

5. **Enable request caching**:
```bash
# Update index settings
curl -X PUT "localhost:9200/research_assistant/_settings" \
  -H 'Content-Type: application/json' \
  -d '{
    "index.requests.cache.enable": true,
    "index.queries.cache.enabled": true
  }'
```

---

### High Disk I/O

**Symptoms**:
- Slow search and indexing
- High disk usage in `docker stats`

**Solutions**:

1. **Increase refresh interval**:
```python
# Reduce index refresh frequency
client.indices.put_settings(
    index='research_assistant',
    body={
        "index": {
            "refresh_interval": "30s"  # Default is 1s
        }
    }
)

# Disable during bulk indexing
client.indices.put_settings(
    index='research_assistant',
    body={"index": {"refresh_interval": "-1"}}
)

# Re-enable after indexing
client.indices.put_settings(
    index='research_assistant',
    body={"index": {"refresh_interval": "1s"}}
)
```

2. **Force merge segments**:
```bash
# Reduce number of segments
curl -X POST "localhost:9200/research_assistant/_forcemerge?max_num_segments=1"
```

---

## Memory Issues

### Out of Memory Errors

**Symptoms**:
- `OutOfMemoryError: Java heap space`
- Container crashes
- Degraded performance

**Diagnosis**:
```bash
# Check memory usage
docker stats opensearch-node

# Check JVM heap
curl http://localhost:9200/_nodes/stats/jvm?pretty
```

**Solutions**:

1. **Increase heap size**:
```bash
docker run -d \
  --name opensearch-node \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "OPENSEARCH_JAVA_OPTS=-Xms2g -Xmx2g" \
  --memory=4g \
  opensearchproject/opensearch:latest
```

2. **Reduce field data cache**:
```bash
curl -X PUT "localhost:9200/_cluster/settings" \
  -H 'Content-Type: application/json' \
  -d '{
    "persistent": {
      "indices.fielddata.cache.size": "20%"
    }
  }'
```

3. **Clear caches**:
```bash
# Clear field data cache
curl -X POST "localhost:9200/_cache/clear?fielddata=true"

# Clear query cache
curl -X POST "localhost:9200/_cache/clear?query=true"

# Clear all caches
curl -X POST "localhost:9200/_cache/clear"
```

4. **Optimize index settings**:
```python
index_settings = {
    "settings": {
        "number_of_shards": 1,  # Reduce for single-node
        "number_of_replicas": 0,  # No replicas for local dev
        "codec": "best_compression"  # Trade CPU for memory
    }
}
```

---

## Cluster Health

### Cluster Health is Yellow or Red

**Symptoms**:
- Yellow cluster status
- Red cluster status
- Unassigned shards

**Diagnosis**:
```bash
# Check cluster health
curl http://localhost:9200/_cluster/health?pretty

# Check shard allocation
curl http://localhost:9200/_cat/shards?v

# Get allocation explanation
curl http://localhost:9200/_cluster/allocation/explain?pretty
```

**Solutions**:

1. **Yellow status (unassigned replicas)**:
```bash
# Normal for single-node cluster
# Set replicas to 0
curl -X PUT "localhost:9200/research_assistant/_settings" \
  -H 'Content-Type: application/json' \
  -d '{"index": {"number_of_replicas": 0}}'
```

2. **Red status (missing primary shards)**:
```bash
# Try to reroute shards
curl -X POST "localhost:9200/_cluster/reroute?retry_failed=true"

# If that fails, may need to restore from snapshot
```

3. **Enable shard allocation**:
```bash
curl -X PUT "localhost:9200/_cluster/settings" \
  -H 'Content-Type: application/json' \
  -d '{
    "persistent": {
      "cluster.routing.allocation.enable": "all"
    }
  }'
```

---

## Index Corruption

### Corrupt Index or Shards

**Symptoms**:
- `CorruptIndexException`
- Missing or corrupted data
- Search returns incomplete results

**Diagnosis**:
```bash
# Check index health
curl http://localhost:9200/_cat/indices/research_assistant?v

# Verify shard status
curl http://localhost:9200/_cat/shards/research_assistant?v
```

**Solutions**:

1. **Close and reopen index**:
```bash
curl -X POST "localhost:9200/research_assistant/_close"
curl -X POST "localhost:9200/research_assistant/_open"
```

2. **Try to recover**:
```bash
curl -X POST "localhost:9200/_cluster/reroute?retry_failed=true"
```

3. **Recreate index from source data**:
```python
# Delete corrupted index
client.indices.delete(index='research_assistant')

# Recreate with proper settings
client.indices.create(index='research_assistant', body=index_settings)

# Reindex all documents
# Run your data collection and indexing pipeline again
```

---

## Diagnostic Commands

### Essential Health Checks

```bash
# Cluster health overview
curl http://localhost:9200/_cluster/health?pretty

# Node information
curl http://localhost:9200/_nodes/stats?pretty

# Index statistics
curl http://localhost:9200/_cat/indices?v

# Shard allocation
curl http://localhost:9200/_cat/shards?v

# Pending tasks
curl http://localhost:9200/_cat/pending_tasks?v

# Thread pool stats
curl http://localhost:9200/_cat/thread_pool?v

# Hot threads
curl http://localhost:9200/_nodes/hot_threads
```

### Performance Monitoring

```bash
# Search performance
curl http://localhost:9200/_nodes/stats/indices/search?pretty

# Indexing performance
curl http://localhost:9200/_nodes/stats/indices/indexing?pretty

# Cache statistics
curl http://localhost:9200/_nodes/stats/indices/query_cache,fielddata,request_cache?pretty

# JVM memory
curl http://localhost:9200/_nodes/stats/jvm?pretty

# Disk usage
curl http://localhost:9200/_nodes/stats/fs?pretty
```

### Index Analysis

```bash
# Index settings
curl http://localhost:9200/research_assistant/_settings?pretty

# Index mappings
curl http://localhost:9200/research_assistant/_mapping?pretty

# Index stats
curl http://localhost:9200/research_assistant/_stats?pretty

# Document count
curl http://localhost:9200/research_assistant/_count

# Sample documents
curl -X GET "localhost:9200/research_assistant/_search?size=1&pretty"
```

---

## Preventive Maintenance

### Regular Maintenance Tasks

1. **Monitor cluster health**:
```bash
# Set up monitoring script
#!/bin/bash
while true; do
    curl -s http://localhost:9200/_cluster/health | jq .status
    sleep 60
done
```

2. **Clear old logs**:
```bash
docker logs opensearch-node --tail 1000 > opensearch.log
docker exec opensearch-node find /usr/share/opensearch/logs -mtime +7 -delete
```

3. **Optimize indices regularly**:
```bash
# Weekly optimization
curl -X POST "localhost:9200/research_assistant/_forcemerge?max_num_segments=1"
```

4. **Backup important indices**:
```bash
# Create snapshot repository
curl -X PUT "localhost:9200/_snapshot/backup" \
  -H 'Content-Type: application/json' \
  -d '{
    "type": "fs",
    "settings": {
      "location": "/usr/share/opensearch/backup"
    }
  }'

# Create snapshot
curl -X PUT "localhost:9200/_snapshot/backup/snapshot_1?wait_for_completion=true"
```

---

## Additional Resources

- [Common Issues](./common-issues.md)
- [Performance Optimization](../advanced/performance.md)
- [OpenSearch Documentation](https://opensearch.org/docs/latest/)
- [FAQ](./faq.md)

## Getting Help

For OpenSearch-specific issues:
1. Check OpenSearch logs: `docker logs opensearch-node`
2. Enable debug logging: Set `OPENSEARCH_JAVA_OPTS` with `-Xlog:gc*`
3. Visit OpenSearch forums: https://forum.opensearch.org/
4. Check GitHub issues: https://github.com/opensearch-project/OpenSearch
