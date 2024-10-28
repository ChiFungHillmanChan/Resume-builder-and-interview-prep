def find_min(nums):
    # Your code here
    return 1

# Test runner
import json
results = []

try:
    result = find_min({"nums": [3, 4, 5, 1, 2]})
    results.append({"index": 0, "actual_output": result, "expected": 1, "passed": result == 1})
except Exception as e:
    results.append({"index": 0, "actual_output": str(e), "expected": 1, "passed": False})

try:
    result = find_min({"nums": [4, 5, 6, 7, 0, 1, 2]})
    results.append({"index": 1, "actual_output": result, "expected": 0, "passed": result == 0})
except Exception as e:
    results.append({"index": 1, "actual_output": str(e), "expected": 0, "passed": False})

print(json.dumps(results))
