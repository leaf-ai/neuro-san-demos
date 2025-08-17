# Performance Benchmarking and Best Practices

This project now supports asynchronous background queries and in-memory caching for
vector and graph operations.  To measure the impact of these features:

1. Run the provided benchmark script:

```bash
python benchmark.py
```

2. The script times a series of cached vector and graph queries.  Repeated
   executions should remain fast because results are served from cache and heavy
   calls run in background threads.

## Best Practices

- Use the `aquery` and `arun_query` helpers to offload long-running operations
  without blocking the main thread.
- Cache lookups are invalidated automatically whenever underlying data is
  modified.
- For manual benchmarking, wrap calls with `time.perf_counter` and compare cached
  versus uncached execution.
