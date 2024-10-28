def two_sum(nums, target):
    # Your code here
    for i in range(len(nums)):
        for j in range(i+1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []

# Test runner
import json
results = []

try:
    result = two_sum(nums=[2, 7, 11, 15], target=9)
    results.append({"index": 0, "actual_output": result, "expected": [0, 1], "passed": result == [0, 1]})
except Exception as e:
    results.append({"index": 0, "actual_output": str(e), "expected": [0, 1], "passed": False})

try:
    result = two_sum(nums=[3, 2, 4], target=6)
    results.append({"index": 1, "actual_output": result, "expected": [1, 2], "passed": result == [1, 2]})
except Exception as e:
    results.append({"index": 1, "actual_output": str(e), "expected": [1, 2], "passed": False})

try:
    result = two_sum(nums=[3, 3], target=6)
    results.append({"index": 2, "actual_output": result, "expected": [0, 1], "passed": result == [0, 1]})
except Exception as e:
    results.append({"index": 2, "actual_output": str(e), "expected": [0, 1], "passed": False})

print(json.dumps(results))
