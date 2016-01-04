import pytest

from AlgoBench.benchmark import Benchmark, AlgoBenchError

class TestStatisticalCalculations():

    #apiKeyRequired = pytest.mark.skipif(
    #not pytest.config.getoption("--runApiKeyTests"),
    #reason="need --runApiKeyTests option to run"
    #)

    def testCalcAverage(self):
        settings = {}
        settings["apiKey"] = "xxx"
        settings["inputSingle"] = "an input"
        settings["algoSingle"] = "userName/algoName"
        b = Benchmark(settings)

        b.results = [{"response":{"metadata":{"duration":0.24214214}}, "algo":"userName/algoName"},\
                     {"response":{"metadata":{"duration":0.43523423}}, "algo":"userName/algoName"},\
                     {"response":{"metadata":{"duration":0.12435256}}, "algo":"userName/algoName"},\
                     {"response":{"metadata":{"duration":0.35314251}}, "algo":"userName/algoName"},\
                     {"response":{"metadata":{"duration":0.12451533}}, "algo":"userName/algoName"}]
        b._Benchmark__calcAverage()

        assert b.average["userName/algoName"] == 0.255877354

    def testCalcUncertainty(self):
        settings = {}
        settings["apiKey"] = "xxx"
        settings["inputSingle"] = "an input"
        settings["algoSingle"] = "userName/algoName"
        b = Benchmark(settings)

        b.results = [{"response":{"metadata":{"duration":0.24214214}}, "algo":"userName/algoName"},\
                     {"response":{"metadata":{"duration":0.43523423}}, "algo":"userName/algoName"},\
                     {"response":{"metadata":{"duration":0.12435256}}, "algo":"userName/algoName"},\
                     {"response":{"metadata":{"duration":0.35314251}}, "algo":"userName/algoName"},\
                     {"response":{"metadata":{"duration":0.12451533}}, "algo":"userName/algoName"}]
        b._Benchmark__calcAverage()
        b._Benchmark__calcUncertainty()

        assert b.uncertainty["userName/algoName"] == 0.15544083

    def testHasNoLabels(self):
        settings = {}
        settings["apiKey"] = "xxx"
        settings["algoSingle"] = "userName/algoName"
        settings["inputSingle"] = "an input"

        b = Benchmark(settings)

        b.results = [{"result": 5, "label": None}, {"result": 7, "label": None}]

        assert b._Benchmark__hasLabels() == False

    def testHasPartialLabels(self):
        settings = {}
        settings["apiKey"] = "xxx"
        settings["algoSingle"] = "userName/algoName"
        settings["inputSingle"] = "an input"

        b = Benchmark(settings)

        b.results = [{"result": 5, "label": 5}, {"result": 7, "label": None}]

        assert b._Benchmark__hasLabels() == False

    def testHasLabels(self):
        settings = {}
        settings["apiKey"] = "xxx"
        settings["algoSingle"] = "userName/algoName"
        settings["inputSingle"] = "an input"

        b = Benchmark(settings)

        b.results = [{"result": 5, "label": 5}, {"result": 7, "label": 7}]

        assert b._Benchmark__hasLabels() == True

    def testCalcBasics(self):
        settings = {}
        settings["apiKey"] = "xxx"
        settings["algoSingle"] = "userName/algoName"
        settings["inputSingle"] = "an input"

        b = Benchmark(settings)

        b.results = [{"result": 5, "label": 5}, {"result": 7, "label": 7},\
                     {"result": 5, "label": 5}, {"result": 1, "label": 7},\
                     {"result": 3, "label": 5}, {"result": 7, "label": 7},\
                     {"result": 5, "label": 5}, {"result": 4, "label": 7},\
                     {"result": 4, "label": 5}, {"result": 7, "label": 7}]

        def mapFunc(res):
            return res

        b.calcStats(mapFunc)

        assert b.stats["FN"]["labels"][5] == 2
        assert b.stats["FN"]["labels"][7] == 2
        assert b.stats["FP"]["labels"][5] == 0
        assert b.stats["FP"]["labels"][7] == 0
        assert b.stats["TN"]["labels"][5] == 5
        assert b.stats["TN"]["labels"][7] == 5
        assert b.stats["TP"]["labels"][5] == 3
        assert b.stats["TP"]["labels"][7] == 3

    def testCalcAccuracy(self):
        settings = {}
        settings["apiKey"] = "xxx"
        settings["algoSingle"] = "userName/algoName"
        settings["inputSingle"] = "an input"

        b = Benchmark(settings)

        b.results = [{"result": 5, "label": 5}, {"result": 7, "label": 7},\
                     {"result": 5, "label": 5}, {"result": 1, "label": 7},\
                     {"result": 3, "label": 5}, {"result": 7, "label": 7},\
                     {"result": 5, "label": 5}, {"result": 4, "label": 7},\
                     {"result": 4, "label": 5}, {"result": 7, "label": 7}]

        def mapFunc(res):
            return res

        b.calcStats(mapFunc)

        assert b.stats['accuracy']['overall'] == 0.75
        assert b.stats['accuracy']['labels'][5] == 0.8
        assert b.stats['accuracy']['labels'][7] == 0.8

    def testCalcPrecision(self):
        settings = {}
        settings["apiKey"] = "xxx"
        settings["algoSingle"] = "userName/algoName"
        settings["inputSingle"] = "an input"

        b = Benchmark(settings)

        b.results = [{"result": 5, "label": 5}, {"result": 7, "label": 7},\
                     {"result": 5, "label": 5}, {"result": 1, "label": 7},\
                     {"result": 3, "label": 5}, {"result": 7, "label": 7},\
                     {"result": 5, "label": 5}, {"result": 4, "label": 7},\
                     {"result": 4, "label": 5}, {"result": 7, "label": 7}]

        def mapFunc(res):
            return res

        b.calcStats(mapFunc)

        assert b.stats['precision']['labels'][5] == 1.0
        assert b.stats['precision']['labels'][7] == 1.0

    def testCalcRecall(self):
        settings = {}
        settings["apiKey"] = "xxx"
        settings["algoSingle"] = "userName/algoName"
        settings["inputSingle"] = "an input"

        b = Benchmark(settings)

        b.results = [{"result": 5, "label": 5}, {"result": 7, "label": 7},\
                     {"result": 5, "label": 5}, {"result": 1, "label": 7},\
                     {"result": 3, "label": 5}, {"result": 7, "label": 7},\
                     {"result": 5, "label": 5}, {"result": 4, "label": 7},\
                     {"result": 4, "label": 5}, {"result": 7, "label": 7}]

        def mapFunc(res):
            return res

        b.calcStats(mapFunc)

        assert b.stats['recall']['labels'][5] == 0.6
        assert b.stats['recall']['labels'][7] == 0.6

    def testCalcFScore(self):
        settings = {}
        settings["apiKey"] = "xxx"
        settings["algoSingle"] = "userName/algoName"
        settings["inputSingle"] = "an input"

        b = Benchmark(settings)

        b.results = [{"result": 5, "label": 5}, {"result": 7, "label": 7},\
                     {"result": 5, "label": 5}, {"result": 1, "label": 7},\
                     {"result": 3, "label": 5}, {"result": 7, "label": 7},\
                     {"result": 5, "label": 5}, {"result": 4, "label": 7},\
                     {"result": 4, "label": 5}, {"result": 7, "label": 7}]

        def mapFunc(res):
            return res

        b.calcStats(mapFunc)

        assert b.stats['fScore']['labels'][5] == 0.7499999999999999
        assert b.stats['fScore']['labels'][7] == 0.7499999999999999