import pytest

from AlgoBench.benchmark import Benchmark, AlgoBenchError

class TestSettingsValidation():

    def testSettingsIsNotDict(self):
        settings = "not dict"
        with pytest.raises(AlgoBenchError):
            b = Benchmark(settings)

    def testNoAPIKey(self):
        settings = {}
        settings["inputSingle"] = "an input"
        settings["algoSingle"] = "userName/algoName"
        with pytest.raises(AlgoBenchError):
            b = Benchmark(settings)

    def testNoInput(self):
        settings = {}
        settings["apiKey"] = "xxx"
        settings["algoSingle"] = "userName/algoName"
        with pytest.raises(AlgoBenchError):
            b = Benchmark(settings)

    def testNoAlgo(self):
        settings = {}
        settings["apiKey"] = "xxx"
        settings["inputSingle"] = "an input"
        with pytest.raises(AlgoBenchError):
            b = Benchmark(settings)

    def testInputSingleProperlyInitialized(self):
        settings = {}
        settings["apiKey"] = "xxx"
        settings["algoSingle"] = "userName/algoName"
        settings["inputSingle"] = "an input"
        b = Benchmark(settings)

        assert "inputLabelList" in b.settings
        assert "inputSingle" not in b.settings

    def testInputListProperlyInitialized(self):
        settings = {}
        settings["apiKey"] = "xxx"
        settings["algoSingle"] = "userName/algoName"
        settings["inputList"] = "an input"
        with pytest.raises(AlgoBenchError):
            b = Benchmark(settings)

        settings["inputList"] = ["an input", "another input"]

        b2 = Benchmark(settings)

        assert "inputLabelList" in b2.settings
        assert "inputList" not in b2.settings

    def testInputLabelListProperlyInitialized(self):
        settings = {}
        settings["apiKey"] = "xxx"
        settings["algoSingle"] = "userName/algoName"
        settings["inputLabelList"] = "an input"

        with pytest.raises(AlgoBenchError):
            b = Benchmark(settings)

        settings["inputLabelList"] = ["an input", "another input"]

        with pytest.raises(AlgoBenchError):
            b2 = Benchmark(settings)

        settings["inputLabelList"] = [{"data":"an input", "label": "true"}, {"data":"another input", "label": "false"}]

        b3 = Benchmark(settings)

        assert "inputLabelList" in b3.settings
        assert "inputList" not in b3.settings
        assert "inputSingle" not in b3.settings

    def testAlgoSingleProperlyInitialized(self):
        settings = {}
        settings["apiKey"] = "xxx"
        settings["algoSingle"] = "userName/algoName"
        settings["inputSingle"] = "an input"

        b = Benchmark(settings)

        assert "algoList" in b.settings
        assert "algoSingle" not in b.settings

    def testAlgoListProperlyInitialized(self):
        settings = {}
        settings["apiKey"] = "xxx"
        settings["algoList"] = "userName/algoName"
        settings["inputSingle"] = "an input"

        with pytest.raises(AlgoBenchError):
            b = Benchmark(settings)

        settings["algoList"] = ["userName/algoName/ver1", "userName/algoName/ver2"]

        b2 = Benchmark(settings)

        assert "algoList" in b2.settings

    def testNoNumBenchRuns(self):
        settings = {}
        settings["apiKey"] = "xxx"
        settings["inputSingle"] = "an input"
        settings["algoSingle"] = "userName/algoName"
        settings["maxNumConnections"] = 12
        b = Benchmark(settings)

        assert b.settings["numBenchRuns"] == 1

    def testNoMaxNumConnections(self):
        settings = {}
        settings["apiKey"] = "xxx"
        settings["inputSingle"] = "an input"
        settings["algoSingle"] = "userName/algoName"
        settings["numBenchRuns"] = 5
        b = Benchmark(settings)

        assert b.settings["maxNumConnections"] == 10