# Algorithmia Benchmark Tester (beta)

[![Travis](https://img.shields.io/travis/algorithmiaio/algorithmia-bench.svg)](https://travis-ci.org/algorithmiaio/algorithmia-bench)
[![PyPi](https://img.shields.io/pypi/v/algorithmia-bench.svg)](https://pypi.python.org/pypi/algorithmia-bench)

Algorithmia Benchmark Tester is a library for testing algorithm performance, comparing algorithms and getting statistical information for each benchmark run. The library also creates certain visualizations (not implemented yet) and gives you a high level idea of how your algorithms perform with different parameters.

## Features

- Can calculate the average run time and the uncertainty for the benchmark.
- Can make multiple algorithm calls asynchronously, which makes very large input processing a lot easier and faster.
- For each label (also known as class or category) it can calculate the accuracy, precision, recall and F1 Score. It can also calculate the general algorithm accuracy.
- Can group different algorithm version together in the benchmark for easy comparison.
- `Not Implemented Yet` Can create visualizations from results such as histograms, pie charts, etc.

## 1. Installation
### 1.1 Install from PyPi
```bash
pip install algorithmia-bench
```
### 1.2 Install from source
Build algorithmia-bench wheel:
```bash
python setup.py bdist_wheel
```
Install wheel manually:
```bash
pip install --user --upgrade dist/algorithmia-*.whl
```


## 2. Getting Started

### 2.1 Settings
Before we can run a benchmark, we need to define the settings. The settings is a dictionary object with required and optional parameters:
- **(Required)** Algorithmia API Key.
  - Format 1:
    - Key: `apiKey`
    - Type: `String`
- **(Required)** Input. It could be any python object (String, List, Dictionary, Tuple, etc.). It should be one of the 3 formats below. Only one format can be passed at a time.
  - Format 1:
    - Key: `inputSingle`
    - Type: `inputObject`
  - Format 2:
    - Key: `inputList`
    - Type: `[inputObject1, ...,inputObjectN]`
  - Format 3:
    - Key: `inputLabelList`
    - Type: `[{"data":inputObject1, "label":label1}, ..., {"data":inputObjectN, "label":labelN}]`

- **(Required)** A single or group of algorithms. Can be only one of the given 2 formats.
  - Format 1:
    - Key: `algoSingle`
    - Type: `String`
  - Format 2: Can be only called with `inputSingle`
    - Key: `algoList`
    - Type: `[String, ..., String]`

- **(Optional)** The number of times you want to re-run on a single iteration. This may be used to get a smoother distribution of average running time.
  - Format 1:
    - Key: `numBenchRuns`
    - Type: `Integer`
    - Default Value: `1`

- **(Optional)** The maximum number of parallel requests made at a time.
  - Format 1:
    - Key: `maxNumConnections`
    - Type: `Integer`
    - Default Value: `10`

### 2.2 Calculate Stats
After running a benchmark with labelled data, we can calculate the accuracy, precision, recall and F1 Score for each label.

The benchmark keeps the results and labels in the `Benchmark.results` property. The format of this property is the following:
```python
Benchmark.results = [
    {"response": algoJSONResponseBody, "label": label},
    ...
    {"response": algoJSONResponseBody, "label": label},
]
```
Before calculating the stats for the benchmark, we need to pass a mapping function which selects the results and labels for comparision from `Benchmark.results`, and returns the corresponding results and labels.

Here's an example mapping function:
```python
def customMappingFunc(results):
    label = results["label"]
    result = results["response"]["result"][0]
    return {"result": result, "label": label}
```

We pass the custom mapping function to calculate the stats for the benchmark.

```python
# b = Benchmark(settings) has been already initialized
b.calcStats(customMappingFunc)
```

After calculating the stats, we can access the following in `b.stats`:
* True Positive for each label in `b.stats["TP"]`
* False Positive for each label in `b.stats["FP"]`
* True Negative for each label in `b.stats["TN"]`
* False Negative for each label in `b.stats["FN"]`
* Accuracy for each label and overall Accuracy in `b.stats["accuracy"]`
* Precision for each label in `b.stats["precision"]`
* Recall for each label in `b.stats["recall"]`
* F1 Score for each label in `b.stats["fScore"]`
* Each available label in `b.stats["labels"]`

## 3. Examples
### 3.1 Basic Usage Example
Example of running a benchmark of 100 times to get the average running time and the associated uncertainty.
```python
from AlgoBench.benchmark import Benchmark

# Our benchmark settings
settings = {
    "apiKey": "xxxxx",
    "inputSingle": "A random tweet from #POTUS",
    "algoSingle": "nlp/SocialSentimentAnalysis",
    "numBench": 100
}

# We run our benchmark
b = Benchmark(settings)

strAverage = str(b.average["nlp/SocialSentimentAnalysis"])
strUncertainty = str(b.uncertainty["nlp/SocialSentimentAnalysis"])

# Get average running time and uncertainty
print "Average running time: " + strAverage + " ±" + strUncertainty
```
### 3.2 Advanced Usage Example 1
Example of comparing different algorithm versions to each other.
```python
from AlgoBench.benchmark import Benchmark

# Our benchmark settings
settings = {
    "apiKey": "xxxxx",
    "inputSingle": "A random tweet from #POTUS",
    "algoList": [
        "nlp/SocialSentimentAnalysis/version1Hash",
        "nlp/SocialSentimentAnalysis/version2Hash",
        "nlp/SocialSentimentAnalysis/version3Hash",
        "nlp/SocialSentimentAnalysis/version4Hash",
        "nlp/SocialSentimentAnalysis/version5Hash"
    ],
    "numBench": 100
}

# We run our benchmark
b = Benchmark(settings)

# Compare benchmark results for different algorithm versions
for algoVersion in b.average:
    strAverage = str(b.average[algoVersion])
    strUncertainty = str(b.uncertainty[algoVersion])
    print "Average for " + algoVersion + " is: " + strAverage
    print "Uncertainty for " + algoVersion + " is: " + strUncertainty
```
### 3.3 Advanced Usage Example 2
Example of loading labelled data and calculating F1 Score for each category.
```python
from AlgoBench.benchmark import Benchmark
import operator


# Our benchmark settings
settings = {
    "apiKey": "xxxxx",
    "inputLabelList": [
        # 5 is positive, 3 is neutral and 1 is negative
        {"data": "a happy tweet", "label": 5},
        {"data": "a sad tweet", "label": 3},
        ...
        {"data": "a neutral tweet", "label": 1}
    ],
    "algoSingle": "nlp/SocialSentimentAnalysis",
    "numBench": 1,
    "maxNumConnections": 15
}

# We run our benchmark
b = Benchmark(settings)

# Our custom mapping function
def customMappingFunc(res):
    label = res['label']
    result = res['response']['result'][0]
    # Remove unnecessary keys from algo result
    result.pop("sentence", None)
    result.pop("compound", None)

    # Returns the prediction with the highest confidence value
    prediction = max(result.iteritems(), key=operator.itemgetter(1))[0]

    if prediction == "neutral":
        corresponding_prediction = 3
    elif prediction == "positive":
        corresponding_prediction = 5
    elif prediction == "negative":
        corresponding_prediction = 1

    return {'result': corresponding_prediction, 'label': label}

# We calculate the stats for this benchmark
b.calcStats(customMappingFunc)

# We print F1 Score's for all labels
for label in b.stats["fScore"]["labels"]:
    fScore = b.stats["fScore"]["labels"][label]
    print "F1 Score for " + str(label) + " is: " + str(fScore)
```