import Algorithmia
import threading
from Algorithmia.algorithm import algorithm
from decimal import Decimal

def pipe(self, input1):
    responseJson = self.client.postJsonHelper(self.url, input1)

    # Parse response JSON
    if 'error' in responseJson:
        # Failure
        raise Exception(responseJson['error']['message'])
    else:
        # Success, check content_type
        if responseJson['metadata']['content_type'] == 'binary':
            # Decode Base64 encoded binary file
            return base64.b64decode(responseJson['result'])
        elif responseJson['metadata']['content_type'] == 'void':
            return None
        else:
            return responseJson

# This is a monkey patch
# Override default pipe method to return full JSON response
algorithm.pipe = pipe

threadLimiter = None

class AlgoBenchError(Exception):
     def __init__(self, value):
         self.value = value
     def __str__(self):
         return repr(self.value)

class Benchmark(object):
    def __init__(self, settings):
        self.results = []
        self.average = {}
        self.uncertainty = {}
        self.threadCount = 0
        self.currentThread = 0
        self.processedThread = 0
        self.threads = []
        self.maxThreadPool = 200

        self.settings = settings

        self.stats = {}
        self.stats["labels"] = []
        self.stats["TP"] = {"labels": {}}
        self.stats["FP"] = {"labels": {}}
        self.stats["TN"] = {"labels": {}}
        self.stats["FN"] = {"labels": {}}
        self.stats["accuracy"] = {"overall": 0, "labels": {}}
        self.stats["recall"] ={"labels": {}}
        self.stats["precision"] = {"labels": {}}
        self.stats["fScore"] = {"labels": {}}

        self.__validateSettings(settings)

    def __validateSettings(self, settings):
        '''
        Description: Validates settings and autmatically coverts input and algo parameters into
            the internally used format (for input it's inputLabelList, for algo it's algoList)

        Example settings:
            settings = {
                "apiKey": "xxx",
                "numBenchRuns": 1,
                "maxNumConnections": 10,
                "inputList": [inputs] or "inputLabelList: [{"data": data, "label": label},...]" or "inputSingle": input,
                "algoList": [algos] or "algoSingle": algo
                    }
        '''
        # Input validation and error handling
        if not isinstance(settings, dict):
            raise AlgoBenchError('Please provide valid settings (dict)')

        if 'apiKey' not in settings:
            raise AlgoBenchError('Please provide an apiKey')

        if 'numBenchRuns' not in settings:
            # default is 1
            settings['numBenchRuns'] = 1
        else:
            if not isinstance(settings['numBenchRuns'], int):
                raise AlgoBenchError('Number of numBenchRuns should be an integer.')
            elif settings['numBenchRuns'] <= 0:
                raise AlgoBenchError('numBenchRuns should be at least 1')

        if 'maxNumConnections' not in settings:
            # default is 10
            settings['maxNumConnections'] = 10
        else:
            if not isinstance(settings['maxNumConnections'], int):
                raise AlgoBenchError('Number of maxNumConnections should be an integer.')
            elif settings['maxNumConnections'] <= 0:
                raise AlgoBenchError('maxNumConnections should be at least 1')

        if 'algoList' not in settings and 'algoSingle' not in settings:
            raise AlgoBenchError('Please provide at least one algo')
        elif 'algoList' in settings and 'algoSingle' in settings:
            raise AlgoBenchError('You cannot provide algoList and algoSingle at the same time')
        elif 'algoList' in settings:
            if 'inputList' in settings:
                raise AlgoBenchError('You cannot provide algoList and inputList at the same time')
            elif 'inputLabelList' in settings:
                raise AlgoBenchError('You cannot provide algoList and inputLabelList at the same time')

        if 'inputList' not in settings and 'inputSingle' not in settings and 'inputLabelList' not in settings:
            raise AlgoBenchError('Please provide an input')
        elif 'inputList' in settings and 'inputSingle' in settings:
            raise AlgoBenchError('You cannot provide inputList and inputSingle at the same time')
        elif 'inputSingle' in settings and 'inputLabelList' in settings:
            raise AlgoBenchError('You cannot provide inputSingle and inputLabelList at the same time')
        elif 'inputList' in settings and 'inputLabelList' in settings:
            raise AlgoBenchError('You cannot provide inputList and inputLabelList at the same time')
        elif 'inputList' in settings and 'inputSingle' in settings and 'inputLabelList' in settings:
            raise AlgoBenchError('You cannot provide inputList, inputSingle and inputLabelList at the same time')
        elif 'inputList' in settings:
            if not isinstance(settings['inputList'], list):
                raise AlgoBenchError('Please provide inputList as a list')
        elif 'inputLabelList' in settings:
            if not isinstance(settings['inputLabelList'], list):
                raise AlgoBenchError('Please provide inputLabelList as a list')
            elif isinstance(settings['inputLabelList'], list):
                for item in settings['inputLabelList']:
                    if not isinstance(item, dict):
                        raise AlgoBenchError('Please properly format your inputLabelList as a dictionary')
                    if 'label' not in item:
                        raise AlgoBenchError('Please properly put a label on each input')

        if 'algoSingle' in settings:
            settings['algoList'] = [settings.pop('algoSingle')]
        if 'algoList' in settings:
            if not isinstance(settings['algoList'], list):
                raise AlgoBenchError('Please provide algoList as a list')
        if 'inputSingle' in settings:
            settings['inputLabelList'] = [{"data": settings.pop('inputSingle'), "label": None}]
        if 'inputList' in settings:
            settings['inputLabelList'] = map(lambda item: {"data": item, "label": None}, settings.pop('inputList'))

    def __validateMappingFunc(self, algoResults):
        for res in algoResults:
            if 'result' in res and 'label' in res and len(res) == 2:
                pass
            else:
                raise AlgoBenchError('Please provide a mapping function which returns in the valid format')

    def run(self):
        apiKey = self.settings['apiKey']
        numBenchRuns = self.settings['numBenchRuns']
        global threadLimiter
        threadLimiter = threading.BoundedSemaphore(self.settings['maxNumConnections'])
        inputLabelList = self.settings['inputLabelList']
        algoList = self.settings['algoList']

        if len(algoList) > 1:
            # Run different algo versions over the same input data
            input = inputLabelList[0]["data"]
            label = inputLabelList[0]["label"]
            self.threadCount = len(algoList) * numBenchRuns
            for algo in algoList:
                self.__addThreads(apiKey, algo, input, label, numBenchRuns)
                self.currentThread += 1
        elif len(inputLabelList) > 1:
            # Run different inputs over the same algo
            algo = algoList[0]
            self.threadCount = len(inputLabelList) * numBenchRuns
            for item in inputLabelList:
                input = item["data"]
                label = item["label"]
                self.__addThreads(apiKey, algo, input, label, numBenchRuns)
                self.currentThread += 1
        elif len(inputLabelList) == 1:
            #Run for single input and single algo
            algo = algoList[0]
            input = inputLabelList[0]["data"]
            label = inputLabelList[0]["label"]
            self.threadCount = numBenchRuns
            self.__addThreads(apiKey, algo, input, label, numBenchRuns)
            self.currentThread += 1
        self.__processThreads()

    def calcStats(self, mapFunc):
        '''
        Description: Calculates certain stats like accuracy, recall, precision,
            f-score etc. Requires a mapping function for mapping algorithm results.
            Requires labelled data for calculations. Needs at least 2 classes (binary classification).

        '''
        if not self.__hasLabels():
            raise AlgoBenchError('Cannot evaluate stats because data is unlabeled or is incorrectly labelled (has None amond labels).')

        #algoResults = [{"result": result, "label": label}]
        algoResults = map(mapFunc, self.results)

        self.__validateMappingFunc(algoResults)

        # Calculate basics: TP, TN, FP, FN
        self.__calcBasics(algoResults)
        self.__calcAccuracy(algoResults)
        self.__calcPrecision()
        self.__calcRecall()
        self.__calcFScore()

    def __calcBasics(self, algoResults):
        '''
        Description: True positives, false positives, true negatives and false negatives are calculated.
            OvR (one vs Rest) method is used here for the purpose of the stats calculations needing binary
            classification.
        '''
        for label in self.stats['labels']:
            self.stats['TP']['labels'][label] = 0
            self.stats['FP']['labels'][label] = 0
            self.stats['TN']['labels'][label] = 0
            self.stats['FN']['labels'][label] = 0

            for res in algoResults:
                if res['label'] == label:
                    if res['result'] == label:
                        self.stats['TP']['labels'][label] += 1
                    elif res['result'] != label:
                        self.stats['FN']['labels'][label] += 1
                elif res['label'] != label:
                    if res['result'] == label:
                        self.stats['FP']['labels'][label] += 1
                    elif res['result'] != label:
                        self.stats['TN']['labels'][label] += 1

    def __calcAccuracy(self, algoResults):
        # Calculate accuracy for each label/class
        for label in self.stats['labels']:
            TP = self.stats['TP']['labels'][label]
            FP = self.stats['FP']['labels'][label]
            TN = self.stats['TN']['labels'][label]
            FN = self.stats['FN']['labels'][label]
            self.stats['accuracy']['labels'][label] = float(TP + TN)/float(TP + FP + TN + FN)

        # Calculate overall accuracy for the algorithm
        overall_positive = 0
        overall_negative = 0
        for res in algoResults:
            if res['result'] == res['label']:
                overall_positive += 1
            elif res['result'] != res['label']:
                overall_negative += 1

        if float(overall_negative + overall_negative) == 0.0:
            self.stats['accuracy']['overall'] = None
        else:
            self.stats['accuracy']['overall'] = float(overall_positive) / float(overall_negative + overall_negative)

    def __calcPrecision(self):
        # Calculate precision for each label/class
        for label in self.stats['labels']:
            TP = self.stats['TP']['labels'][label]
            FP = self.stats['FP']['labels'][label]
            if float(TP + FP) == 0.0:
                self.stats['precision']['labels'][label] = None
            else:
                self.stats['precision']['labels'][label] = float(TP)/float(TP + FP)

    def __calcRecall(self):
        # Calculate precision for each label/class
        for label in self.stats['labels']:
            TP = self.stats['TP']['labels'][label]
            FN = self.stats['FN']['labels'][label]

            if float(TP + FN) == 0.0:
                self.stats['recall']['labels'][label] = None
            else:
                self.stats['recall']['labels'][label] = float(TP)/float(TP + FN)

    def __calcFScore(self):
        # Calculate F1 Score for each label/class
        for label in self.stats['labels']:
            precision = self.stats['precision']['labels'][label]
            recall = self.stats['recall']['labels'][label]

            try:
                if float(precision+recall) == 0.0:
                    fScore = None
                else:
                    fScore = float(2*precision*recall)/float(precision+recall)

                self.stats['fScore']['labels'][label] = fScore
            except TypeError:
                self.stats['fScore']['labels'][label] = None

    def __hasLabels(self):
        '''
        Description: Tells you if there exists at least 1 unique label. If so, It'll keep a copy
            in self.stats['label']
        '''
        labels = []
        for res in self.results:
            labels.append(res['label'])

        uniqueLabels = list(set(labels))

        if len(uniqueLabels) >= 2 and None not in uniqueLabels:
            self.stats['labels'] = uniqueLabels
            return True
        else:
            return False

    def __addThreads(self, apiKey, algo, input, label, numBenchRuns):
        # Create new pool of threads
        for i in range(numBenchRuns):
            self.threads.append(BenchThread(apiKey, algo, input, label))

    def __processThreads(self):
        '''
        Description: Divides the thread pool into smaller chunks for OS related
            resource restrictions
        '''
        quotient = int(self.threadCount / self.maxThreadPool)
        remainder = self.threadCount % self.maxThreadPool

        # Iterate over each equally sized sub-thread pool + the remaining thread pool
        for i in range(quotient + 1):
            # Only iterate over equally sized sub-thread pools
            if i != quotient:
                for j in range((i*self.maxThreadPool),((i+1)*self.maxThreadPool)):
                    self.threads[j].start()
                for t in self.threads[(i*self.maxThreadPool):((i+1)*self.maxThreadPool)]:
                    t.join()
                    self.processedThread += 1
                    print str(self.processedThread) + "/" + str(self.threadCount)
                    self.results.append({"response": t.response, "algo": t.algo, "label": t.label})
            # Iterate over the remaining thread pool
            else:
                for j in range((i*self.maxThreadPool), i*self.maxThreadPool + remainder):
                    self.threads[j].start()
                for t in self.threads[(i*self.maxThreadPool):(i*self.maxThreadPool + remainder)]:
                    t.join()
                    self.processedThread += 1
                    print str(self.processedThread) + "/" + str(self.threadCount)
                    self.results.append({"response": t.response, "algo": t.algo, "label": t.label})
        # Calculate some stats about the benchmark
        self.__calcAverage()
        self.__calcUncertainty()

    def __calcAverage(self):
        algos = []
        for res in self.results:
            algos.append(res['algo'])

        unique_algos = list(set(algos))

        sum = {}
        total = {}

        for algo in unique_algos:
            sum[algo] = 0
            total[algo] = 0

        for res in self.results:
            algo = res['algo']

            sum[algo] += res['response']['metadata']['duration']
            total[algo] += 1

        for s in sum:
            self.average[s] = sum[s] / total[s]

        # Old code for single overall average
        #sum = 0
        #for res in self.results:
        #    sum += res['response']['metadata']['duration']
        #self.average = sum / len(self.results)

    def __calcUncertainty(self):
        # Reference: https://www.youtube.com/watch?v=riMzriytw40
        algos = []
        for res in self.results:
            algos.append(res['algo'])

        unique_algos = list(set(algos))

        for algo in unique_algos:
            filteredResults = filter(lambda x: x['algo'] == algo, self.results)

            # Get max and min value in self.results
            maxVal = max(filteredResults, key=lambda x: float(x['response']['metadata']['duration']))['response']['metadata']['duration']
            minVal = min(filteredResults, key=lambda x: float(x['response']['metadata']['duration']))['response']['metadata']['duration']

            self.uncertainty[algo] = (maxVal-minVal)/2

            # Calc uncertainty decimal points
            uncDLen = len(str(Decimal(str(self.uncertainty[algo])) % 1).split(".")[1])
            uncDLen -= 1

            # Calc average decimal points
            avrDLen = len(str(Decimal(str(self.average[algo])) % 1).split(".")[1])
            avrDLen -= 1

            # Pick the smaller decimal point
            minDLen = min([uncDLen, avrDLen])

            self.uncertainty[algo] = round(self.uncertainty[algo], minDLen)
            self.average[algo] = round(self.average[algo], minDLen)

class BenchThread(threading.Thread):
    def __init__(self, apiKey, algo, input, label):
        super(BenchThread, self).__init__()
        self.algo = algo
        self.conn = Algorithmia
        self.conn.apiKey = apiKey
        self.input = input
        self.label = label
        self.response = None

    def run(self):
        global threadLimiter
        threadLimiter.acquire()
        try:
            self.response = self.conn.algo(self.algo).pipe(self.input)
        finally:
            threadLimiter.release()